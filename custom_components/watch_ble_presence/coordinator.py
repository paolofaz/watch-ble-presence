"""Coordinator for Watch BLE Presence."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import re
import time

from homeassistant.components import bluetooth
from homeassistant.components.private_ble_device.coordinator import async_last_service_info
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_FRIENDLY_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .const import (
    CONF_PRESENCE_TIMEOUT,
    CONF_UPDATE_INTERVAL,
    DEFAULT_PRESENCE_TIMEOUT,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    PRIVATE_BLE_DOMAIN,
)

_LOGGER = logging.getLogger(__name__)
_MAC_RE = re.compile(r"^(?:[0-9A-F]{2}[:-]){5}[0-9A-F]{2}$", re.IGNORECASE)


@dataclass(frozen=True, slots=True)
class WatchDefinition:
    """Static definition of a tracked Private BLE device."""

    private_entry_id: str
    irk_hex: str
    irk: bytes
    name: str


@dataclass(frozen=True, slots=True)
class WatchState:
    """Latest known BLE state for a watch."""

    detected: bool
    last_seen: datetime | None
    age_seconds: float | None
    rssi: int | None
    source: str | None
    scanner_name: str | None
    address: str | None
    bluetooth_name: str | None


def _looks_like_mac(value: str | None) -> bool:
    return bool(value and _MAC_RE.fullmatch(value.strip()))


def _usable_name(value: str | None) -> bool:
    if not value:
        return False
    value = value.strip()
    if not value or _looks_like_mac(value):
        return False
    lowered = value.lower()
    return lowered not in {
        "ble device tracker",
        "private ble device",
        "mac address",
    } and not lowered.startswith("private ble device ")


def _humanize_object_id(entity_id: str) -> str | None:
    """Use a manually renamed entity id as a last-resort friendly name."""
    try:
        object_id = entity_id.split(".", 1)[1]
    except IndexError:
        return None

    # Avoid turning an automatically generated MAC-ish object id into a fake name.
    compact = object_id.replace("_", "").replace("-", "")
    if len(compact) == 12 and all(ch in "0123456789abcdefABCDEF" for ch in compact):
        return None
    if object_id in {"ble_device_tracker", "private_ble_device", "mac_address"}:
        return None

    return object_id.replace("_", " ").strip().title()


def resolve_watch_name(hass: HomeAssistant, private_entry: ConfigEntry) -> str:
    """Resolve the best human-readable name for a Private BLE config entry."""
    entity_registry = er.async_get(hass)

    # Prefer the official Private BLE device_tracker name/entity_id because users
    # often rename that to e.g. "Apple Watch Paolo".
    for entity_entry in entity_registry.entities.values():
        if entity_entry.config_entry_id != private_entry.entry_id:
            continue
        if not entity_entry.entity_id.startswith("device_tracker."):
            continue

        state = hass.states.get(entity_entry.entity_id)
        candidates = [
            state.attributes.get(ATTR_FRIENDLY_NAME) if state else None,
            entity_entry.name,
            _humanize_object_id(entity_entry.entity_id),
        ]
        for candidate in candidates:
            if _usable_name(candidate):
                return candidate.strip()

    irk_hex = private_entry.data.get("irk", "")
    device_registry = dr.async_get(hass)
    if irk_hex:
        device = device_registry.async_get_device_by_identifier(
            (PRIVATE_BLE_DOMAIN, irk_hex), private_entry.entry_id
        )
        if device is not None:
            for candidate in (device.name_by_user, device.name):
                if _usable_name(candidate):
                    return candidate.strip()

    if _usable_name(private_entry.title):
        return private_entry.title.strip()

    suffix = irk_hex[:6].upper() if irk_hex else private_entry.entry_id[:6].upper()
    return f"Watch BLE {suffix}"


def scanner_friendly_name(hass: HomeAssistant, source: str | None) -> str | None:
    """Return a human-readable scanner name when HA exposes one."""
    if not source:
        return None

    scanner = bluetooth.async_scanner_by_source(hass, source)
    if scanner is not None:
        # Read-only inspection. BaseHaScanner exposes a human-readable name;
        # getattr keeps this best-effort if habluetooth changes in the future.
        name = getattr(scanner, "name", None)
        if isinstance(name, str) and name.strip() and name.strip() != source:
            return name.strip()

    return source


class WatchBleCoordinator(DataUpdateCoordinator[dict[str, WatchState]]):
    """Poll HA's in-memory Bluetooth cache for Private BLE watches."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        watches: list[WatchDefinition],
    ) -> None:
        self.entry = entry
        self.watches = watches
        self.presence_timeout = int(
            entry.options.get(CONF_PRESENCE_TIMEOUT, DEFAULT_PRESENCE_TIMEOUT)
        )
        update_interval = int(
            entry.options.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
        )
        self._states: dict[str, WatchState] = {}

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=update_interval),
        )

    async def _async_update_data(self) -> dict[str, WatchState]:
        """Read the latest cached BLE advertisement for every configured IRK."""
        now_utc = dt_util.utcnow()
        now_monotonic = time.monotonic()
        new_states: dict[str, WatchState] = {}

        for watch in self.watches:
            previous = self._states.get(watch.private_entry_id)
            service_info = async_last_service_info(self.hass, watch.irk)

            if service_info is not None:
                age_seconds = max(0.0, now_monotonic - service_info.time)
                last_seen = now_utc - timedelta(seconds=age_seconds)
                source = service_info.source
                scanner_name = scanner_friendly_name(self.hass, source)
                address = service_info.address
                bluetooth_name = service_info.name
                rssi = service_info.advertisement.rssi
            elif previous is not None:
                last_seen = previous.last_seen
                age_seconds = (
                    max(0.0, (now_utc - last_seen).total_seconds())
                    if last_seen is not None
                    else None
                )
                source = previous.source
                scanner_name = previous.scanner_name
                address = previous.address
                bluetooth_name = previous.bluetooth_name
                rssi = previous.rssi
            else:
                last_seen = None
                age_seconds = None
                source = None
                scanner_name = None
                address = None
                bluetooth_name = None
                rssi = None

            detected = (
                age_seconds is not None and age_seconds <= self.presence_timeout
            )

            new_states[watch.private_entry_id] = WatchState(
                detected=detected,
                last_seen=last_seen,
                age_seconds=age_seconds,
                rssi=rssi,
                source=source,
                scanner_name=scanner_name,
                address=address,
                bluetooth_name=bluetooth_name,
            )

        self._states = new_states
        return new_states

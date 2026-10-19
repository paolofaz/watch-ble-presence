"""Coordinator for Watch BLE Presence."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import time

from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .ble_resolver import async_last_service_info
from .const import CONF_PRESENCE_TIMEOUT, CONF_UPDATE_INTERVAL, DEFAULT_PRESENCE_TIMEOUT, DEFAULT_UPDATE_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class WatchDefinition:
    """Configuration of one watch."""

    watch_id: str
    irk: bytes
    name: str


@dataclass(frozen=True, slots=True)
class WatchState:
    """Last cached Bluetooth state for one watch."""

    detected: bool
    last_seen: datetime | None
    age_seconds: float | None
    rssi: int | None
    source: str | None
    scanner_name: str | None
    address: str | None
    bluetooth_name: str | None


def scanner_friendly_name(hass: HomeAssistant, source: str | None) -> str | None:
    """Return human-readable name of the Bluetooth scanner when available."""
    if not source:
        return None
    scanner = bluetooth.async_scanner_by_source(hass, source)
    if scanner is not None:
        name = getattr(scanner, "name", None)
        if isinstance(name, str) and name.strip() and name.strip() != source:
            return name.strip()
    return source


class WatchBleCoordinator(DataUpdateCoordinator[dict[str, WatchState]]):
    """Poll the existing Bluetooth advertisement cache for configured watches."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, watches: list[WatchDefinition]) -> None:
        self.entry = entry
        self.watches = watches
        self.presence_timeout = int(entry.options.get(CONF_PRESENCE_TIMEOUT, DEFAULT_PRESENCE_TIMEOUT))
        update_interval = int(entry.options.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL))
        self._states: dict[str, WatchState] = {}
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(seconds=update_interval))

    async def _async_update_data(self) -> dict[str, WatchState]:
        """Read the latest BLE advertisement, keeping previous readings when absent."""
        now_utc = dt_util.utcnow()
        now_monotonic = time.monotonic()
        new_states: dict[str, WatchState] = {}

        for watch in self.watches:
            previous = self._states.get(watch.watch_id)
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
                age_seconds = max(0.0, (now_utc - last_seen).total_seconds()) if last_seen is not None else None
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
            detected = age_seconds is not None and age_seconds <= self.presence_timeout
            new_states[watch.watch_id] = WatchState(
                detected=detected, last_seen=last_seen, age_seconds=age_seconds,
                rssi=rssi, source=source, scanner_name=scanner_name,
                address=address, bluetooth_name=bluetooth_name,
            )
        self._states = new_states
        return new_states

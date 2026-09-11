"""Watch BLE Presence integration."""

from __future__ import annotations

import binascii

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import PLATFORMS, PRIVATE_BLE_DOMAIN
from .coordinator import WatchBleCoordinator, WatchDefinition, resolve_watch_name


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Watch BLE Presence from a config entry."""
    watches: list[WatchDefinition] = []

    for private_entry in hass.config_entries.async_entries(PRIVATE_BLE_DOMAIN):
        irk_hex = private_entry.data.get("irk")
        if not irk_hex:
            continue
        try:
            irk = binascii.unhexlify(irk_hex)
        except (binascii.Error, ValueError):
            continue

        watches.append(
            WatchDefinition(
                private_entry_id=private_entry.entry_id,
                irk_hex=irk_hex,
                irk=irk,
                name=resolve_watch_name(hass, private_entry),
            )
        )

    coordinator = WatchBleCoordinator(hass, entry, watches)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Watch BLE Presence."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

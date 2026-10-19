"""Watch BLE Presence integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_WATCHES, PLATFORMS
from .coordinator import WatchBleCoordinator, WatchDefinition

_LOGGER = logging.getLogger(__name__)


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate legacy empty config without reading another integration's IRKs."""
    if entry.version == 1:
        hass.config_entries.async_update_entry(
            entry,
            data={**entry.data, CONF_WATCHES: entry.data.get(CONF_WATCHES, [])},
            version=2,
        )
        _LOGGER.warning(
            "Watch BLE Presence was upgraded: add each watch IRK using Configure; "
            "existing watch entities will not update until their IRKs are configured"
        )
        return True
    return entry.version == 2


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up watches using this integration's own IRKs."""
    watches = [
        WatchDefinition(
            private_entry_id=watch["id"],
            irk_hex=watch["irk"],
            irk=bytes.fromhex(watch["irk"]),
            name=watch["name"],
        )
        for watch in entry.data.get(CONF_WATCHES, [])
    ]

    # The coordinator only reads the shared Home Assistant Bluetooth cache.
    # No extra BLE listener or active scan is necessary.

    coordinator = WatchBleCoordinator(hass, entry, watches)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Watch BLE Presence entities."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

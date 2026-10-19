"""Watch BLE Presence integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_WATCHES, PLATFORMS
from .coordinator import WatchBleCoordinator, WatchDefinition


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Load only Watch BLE Presence's own configuration."""
    watches = [
        WatchDefinition(
            private_entry_id=watch["id"],
            irk_hex=watch["irk"],
            irk=bytes.fromhex(watch["irk"]),
            name=watch["name"],
        )
        for watch in entry.data.get(CONF_WATCHES, [])
    ]
    coordinator = WatchBleCoordinator(hass, entry, watches)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Watch BLE Presence."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

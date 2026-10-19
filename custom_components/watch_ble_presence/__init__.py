"""Watch BLE Presence integration."""

from __future__ import annotations

from homeassistant.components import bluetooth
from homeassistant.components.bluetooth.match import BluetoothCallbackMatcher
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_WATCHES, PLATFORMS
from .coordinator import WatchBleCoordinator, WatchDefinition


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

    # Match the official integration's scanning mode without importing its internals.
    if watches:
        unsubscribe = bluetooth.async_register_callback(
            hass,
            lambda _info, _change: None,
            BluetoothCallbackMatcher(connectable=False),
            bluetooth.BluetoothScanningMode.ACTIVE,
        )
        entry.async_on_unload(unsubscribe)

    coordinator = WatchBleCoordinator(hass, entry, watches)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload entities and release the Bluetooth listener."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        entry.async_unload_callbacks()
    return unloaded

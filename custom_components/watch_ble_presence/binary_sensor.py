"""Binary sensors for Watch BLE Presence."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import WatchBleCoordinator
from .entity import WatchBleEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Watch BLE binary sensors."""
    coordinator: WatchBleCoordinator = entry.runtime_data
    async_add_entities(
        WatchBleDetectedBinarySensor(coordinator, watch)
        for watch in coordinator.watches
    )


class WatchBleDetectedBinarySensor(WatchBleEntity, BinarySensorEntity):
    """True when a watch has been seen within the configured timeout."""

    _attr_translation_key = "detected"
    _attr_device_class = BinarySensorDeviceClass.PRESENCE

    def __init__(self, coordinator, watch) -> None:
        super().__init__(coordinator, watch, "detected")

    @property
    def is_on(self) -> bool:
        return self.watch_state.detected

    @property
    def icon(self) -> str:
        return "mdi:bluetooth-connect" if self.is_on else "mdi:bluetooth-off"

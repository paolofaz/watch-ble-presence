"""Sensors for Watch BLE Presence."""

from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.const import (
    EntityCategory,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    UnitOfTime,
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
    """Set up Watch BLE sensors."""
    coordinator: WatchBleCoordinator = entry.runtime_data
    entities = []
    for watch in coordinator.watches:
        entities.extend(
            [
                WatchBleLastSeenSensor(coordinator, watch),
                WatchBleAgeSensor(coordinator, watch),
                WatchBleRssiSensor(coordinator, watch),
                WatchBleScannerSensor(coordinator, watch),
                WatchBleAddressSensor(coordinator, watch),
                WatchBleNameSensor(coordinator, watch),
            ]
        )
    async_add_entities(entities)


class WatchBleLastSeenSensor(WatchBleEntity, SensorEntity):
    _attr_translation_key = "last_seen"
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, coordinator, watch) -> None:
        super().__init__(coordinator, watch, "last_seen")

    @property
    def native_value(self):
        return self.watch_state.last_seen


class WatchBleAgeSensor(WatchBleEntity, SensorEntity):
    _attr_translation_key = "age"
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 1

    def __init__(self, coordinator, watch) -> None:
        super().__init__(coordinator, watch, "age")

    @property
    def native_value(self):
        value = self.watch_state.age_seconds
        return round(value, 1) if value is not None else None


class WatchBleRssiSensor(WatchBleEntity, SensorEntity):
    _attr_translation_key = "rssi"
    _attr_device_class = SensorDeviceClass.SIGNAL_STRENGTH
    _attr_native_unit_of_measurement = SIGNAL_STRENGTH_DECIBELS_MILLIWATT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, watch) -> None:
        super().__init__(coordinator, watch, "rssi")

    @property
    def native_value(self):
        return self.watch_state.rssi


class WatchBleScannerSensor(WatchBleEntity, SensorEntity):
    _attr_translation_key = "scanner"
    _attr_icon = "mdi:access-point"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, watch) -> None:
        super().__init__(coordinator, watch, "scanner")

    @property
    def native_value(self):
        return self.watch_state.scanner_name


class WatchBleAddressSensor(WatchBleEntity, SensorEntity):
    _attr_translation_key = "address"
    _attr_icon = "mdi:identifier"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, watch) -> None:
        super().__init__(coordinator, watch, "address")

    @property
    def native_value(self):
        return self.watch_state.address


class WatchBleNameSensor(WatchBleEntity, SensorEntity):
    _attr_translation_key = "bluetooth_name"
    _attr_icon = "mdi:bluetooth"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, watch) -> None:
        super().__init__(coordinator, watch, "bluetooth_name")

    @property
    def native_value(self):
        return self.watch_state.bluetooth_name

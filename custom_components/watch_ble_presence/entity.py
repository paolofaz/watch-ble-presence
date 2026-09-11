"""Base entities for Watch BLE Presence."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import WatchBleCoordinator, WatchDefinition, WatchState


class WatchBleEntity(CoordinatorEntity[WatchBleCoordinator]):
    """Base entity tied to one Watch BLE device."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: WatchBleCoordinator,
        watch: WatchDefinition,
        key: str,
    ) -> None:
        super().__init__(coordinator)
        self.watch = watch
        self._attr_unique_id = f"{watch.private_entry_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, watch.private_entry_id)},
            name=watch.name,
            model="Private BLE presence",
        )

    @property
    def watch_state(self) -> WatchState:
        """Return the latest state for this watch."""
        return self.coordinator.data[self.watch.private_entry_id]

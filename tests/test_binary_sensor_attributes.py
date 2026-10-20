"""Check presence departure exposes a last-seen timestamp for HA automations."""

from datetime import datetime, timezone
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

BINARY_SENSOR_FILE = (
    Path(__file__).resolve().parents[1]
    / "custom_components"
    / "watch_ble_presence"
    / "binary_sensor.py"
)


def load_binary_sensor():
    """Import the real binary sensor with minimal Home Assistant stubs."""
    package_name = "watch_ble_binary_sensor_attributes_test"
    package = types.ModuleType(package_name)
    package.__path__ = [str(BINARY_SENSOR_FILE.parent)]

    coordinator = types.ModuleType(package_name + ".coordinator")
    coordinator.WatchBleCoordinator = object

    entity = types.ModuleType(package_name + ".entity")

    class WatchBleEntity:
        def __init__(self, coordinator, watch, key):
            self.coordinator = coordinator
            self.watch = watch

        @property
        def watch_state(self):
            return self.coordinator.data[self.watch.watch_id]

    entity.WatchBleEntity = WatchBleEntity

    ha = types.ModuleType("homeassistant")
    components = types.ModuleType("homeassistant.components")
    bs = types.ModuleType("homeassistant.components.binary_sensor")

    class BinarySensorDeviceClass:
        PRESENCE = "presence"

    class BinarySensorEntity:
        pass

    bs.BinarySensorDeviceClass = BinarySensorDeviceClass
    bs.BinarySensorEntity = BinarySensorEntity
    components.binary_sensor = bs

    core = types.ModuleType("homeassistant.core")
    core.HomeAssistant = object
    helpers = types.ModuleType("homeassistant.helpers")
    entity_platform = types.ModuleType("homeassistant.helpers.entity_platform")
    entity_platform.AddConfigEntryEntitiesCallback = object
    helpers.entity_platform = entity_platform

    modules = {
        package_name: package,
        package_name + ".coordinator": coordinator,
        package_name + ".entity": entity,
        "homeassistant": ha,
        "homeassistant.components": components,
        "homeassistant.components.binary_sensor": bs,
        "homeassistant.core": core,
        "homeassistant.helpers": helpers,
        "homeassistant.helpers.entity_platform": entity_platform,
    }

    with patch.dict(sys.modules, modules):
        spec = importlib.util.spec_from_file_location(
            package_name + ".binary_sensor", BINARY_SENSOR_FILE
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
    return module.WatchBleDetectedBinarySensor


class LastSeenBeforeOffTests(unittest.TestCase):
    def setUp(self):
        sensor_class = load_binary_sensor()
        self.seen_at = datetime(2026, 10, 20, 9, 20, tzinfo=timezone.utc)
        self.watch = types.SimpleNamespace(watch_id="watch-1")
        self.coordinator = types.SimpleNamespace(data={})
        self.sensor = sensor_class(self.coordinator, self.watch)

    def set_state(self, detected, last_seen):
        self.coordinator.data[self.watch.watch_id] = types.SimpleNamespace(
            detected=detected, last_seen=last_seen
        )

    def test_off_exposes_last_seen_before_off(self):
        self.set_state(False, self.seen_at)
        self.assertFalse(self.sensor.is_on)
        self.assertEqual(
            self.sensor.extra_state_attributes["last_seen_before_off"],
            self.seen_at.isoformat(),
        )

    def test_on_does_not_report_departure_time(self):
        self.set_state(True, self.seen_at)
        self.assertTrue(self.sensor.is_on)
        self.assertIsNone(
            self.sensor.extra_state_attributes["last_seen_before_off"]
        )

    def test_never_seen_has_no_departure_time(self):
        self.set_state(False, None)
        self.assertIsNone(
            self.sensor.extra_state_attributes["last_seen_before_off"]
        )


if __name__ == "__main__":
    unittest.main()

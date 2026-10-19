"""Test presence calculation for four Watches using mocked cached advertisements."""

from datetime import datetime, timezone
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

COMPONENT = Path(__file__).resolve().parents[1] / "custom_components" / "watch_ble_presence"


def load_coordinator(read_advertisement):
    """Run the real coordinator with small fake Home Assistant interfaces."""
    package_name = "watch_ble_presence_coordinator_test"
    package = types.ModuleType(package_name)
    package.__path__ = [str(COMPONENT)]
    const = types.ModuleType(package_name + ".const")
    for key, value in {
        "CONF_PRESENCE_TIMEOUT": "presence_timeout",
        "CONF_UPDATE_INTERVAL": "update_interval",
        "DEFAULT_PRESENCE_TIMEOUT": 300,
        "DEFAULT_UPDATE_INTERVAL": 60,
        "DOMAIN": "watch_ble_presence",
    }.items():
        setattr(const, key, value)
    resolver = types.ModuleType(package_name + ".ble_resolver")
    resolver.async_last_service_info = read_advertisement
    ha = types.ModuleType("homeassistant")
    components = types.ModuleType("homeassistant.components")
    bluetooth = types.ModuleType("homeassistant.components.bluetooth")
    bluetooth.async_scanner_by_source = lambda hass, source: types.SimpleNamespace(name="Proxy " + source)
    components.bluetooth = bluetooth
    ha.components = components
    config_entries = types.ModuleType("homeassistant.config_entries")
    config_entries.ConfigEntry = object
    core = types.ModuleType("homeassistant.core")
    core.HomeAssistant = object
    helpers = types.ModuleType("homeassistant.helpers")
    update = types.ModuleType("homeassistant.helpers.update_coordinator")

    class DataUpdateCoordinator:
        def __class_getitem__(cls, item):
            return cls

        def __init__(self, hass, logger, **kwargs):
            self.hass = hass

    update.DataUpdateCoordinator = DataUpdateCoordinator
    helpers.update_coordinator = update
    util = types.ModuleType("homeassistant.util")
    dt = types.ModuleType("homeassistant.util.dt")
    dt.utcnow = lambda: datetime(2026, 10, 19, tzinfo=timezone.utc)
    util.dt = dt
    ha.util = util

    modules = {
        package_name: package,
        package_name + ".const": const,
        package_name + ".ble_resolver": resolver,
        "homeassistant": ha,
        "homeassistant.components": components,
        "homeassistant.components.bluetooth": bluetooth,
        "homeassistant.config_entries": config_entries,
        "homeassistant.core": core,
        "homeassistant.helpers": helpers,
        "homeassistant.helpers.update_coordinator": update,
        "homeassistant.util": util,
        "homeassistant.util.dt": dt,
    }
    with patch.dict(sys.modules, modules):
        spec = importlib.util.spec_from_file_location(
            package_name + ".coordinator", COMPONENT / "coordinator.py"
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
    return module


class PresenceTimeoutTests(unittest.IsolatedAsyncioTestCase):
    async def test_four_independent_watch_states(self):
        def info(age, source):
            return types.SimpleNamespace(
                time=1000.0 - age,
                source=source,
                address="AA:BB",
                name="Watch",
                advertisement=types.SimpleNamespace(rssi=-64),
            )

        advertisements = {
            b"1": info(12, "one"),
            b"2": info(150, "two"),
            b"3": info(390, "three"),
        }
        module = load_coordinator(lambda hass, irk: advertisements.get(irk))
        watches = [
            module.WatchDefinition(private_entry_id=str(i), irk_hex="", irk=str(i).encode(), name="Watch " + str(i))
            for i in range(1, 5)
        ]
        entry = types.SimpleNamespace(options={"presence_timeout": 300, "update_interval": 60})
        coordinator = module.WatchBleCoordinator(object(), entry, watches)
        with patch.object(module.time, "monotonic", return_value=1000.0):
            states = await coordinator._async_update_data()

        self.assertEqual([states[str(i)].detected for i in range(1, 5)], [True, True, False, False])
        self.assertEqual(states["1"].age_seconds, 12)
        self.assertEqual(states["1"].scanner_name, "Proxy one")
        self.assertEqual(states["1"].rssi, -64)
        self.assertIsNone(states["4"].last_seen)


if __name__ == "__main__":
    unittest.main()

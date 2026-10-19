"""Test entry migration without a Home Assistant installation."""

import asyncio
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

COMPONENT = (
    Path(__file__).resolve().parents[1]
    / "custom_components"
    / "watch_ble_presence"
)


def load_integration():
    """Load the real integration with isolated HA API doubles."""
    name = "watch_ble_migration_test"
    pkg = types.ModuleType(name)
    pkg.__path__ = [str(COMPONENT)]
    const = types.ModuleType(name + ".const")
    const.CONF_WATCHES = "watches"
    const.PLATFORMS = ["sensor", "binary_sensor"]
    coordinator = types.ModuleType(name + ".coordinator")

    class WatchDefinition:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    class WatchBleCoordinator:
        instances = []

        def __init__(self, hass, entry, watches):
            self.watches = watches
            self.instances.append(self)

        async def async_config_entry_first_refresh(self):
            pass

    coordinator.WatchBleCoordinator = WatchBleCoordinator
    coordinator.WatchDefinition = WatchDefinition

    ha = types.ModuleType("homeassistant")
    components = types.ModuleType("homeassistant.components")
    bluetooth = types.ModuleType("homeassistant.components.bluetooth")
    bluetooth_match = types.ModuleType("homeassistant.components.bluetooth.match")

    class BluetoothCallbackMatcher(dict):
        pass

    bluetooth_match.BluetoothCallbackMatcher = BluetoothCallbackMatcher
    bluetooth.BluetoothScanningMode = types.SimpleNamespace(ACTIVE="active")
    bluetooth.async_register_callback = lambda *args: (lambda: None)
    components.bluetooth = bluetooth
    ha.components = components

    ce = types.ModuleType("homeassistant.config_entries")
    ce.ConfigEntry = object
    core = types.ModuleType("homeassistant.core")
    core.HomeAssistant = object

    modules = {
        name: pkg,
        name + ".const": const,
        name + ".coordinator": coordinator,
        "homeassistant": ha,
        "homeassistant.components": components,
        "homeassistant.components.bluetooth": bluetooth,
        "homeassistant.components.bluetooth.match": bluetooth_match,
        "homeassistant.config_entries": ce,
        "homeassistant.core": core,
    }
    with patch.dict(sys.modules, modules):
        spec = importlib.util.spec_from_file_location(
            name, COMPONENT / "__init__.py",
            submodule_search_locations=[str(COMPONENT)],
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return module, WatchBleCoordinator


class FakeEntry:
    def __init__(self, version=1, data=None):
        self.version = version
        self.data = data if data is not None else {}
        self.runtime_data = None
        self.callbacks = []

    def async_on_unload(self, callback):
        self.callbacks.append(callback)


class FakeConfigEntries:
    def __init__(self):
        self.updates = []

    def async_update_entry(self, entry, **changes):
        self.updates.append(changes)
        entry.data = changes["data"]
        entry.version = changes["version"]

    async def async_forward_entry_setups(self, entry, platforms):
        pass

    async def async_unload_platforms(self, entry, platforms):
        return True


class MigrationTests(unittest.IsolatedAsyncioTestCase):
    async def test_empty_v1_upgrade_does_not_import_other_irks(self):
        integration, _ = load_integration()
        hass = types.SimpleNamespace(config_entries=FakeConfigEntries())
        entry = FakeEntry(version=1)
        self.assertTrue(await integration.async_migrate_entry(hass, entry))
        self.assertEqual(entry.version, 2)
        self.assertEqual(entry.data, {"watches": []})
        self.assertEqual(len(hass.config_entries.updates), 1)

    async def test_existing_watch_id_used_for_entity_identity(self):
        integration, coordinator = load_integration()
        hass = types.SimpleNamespace(config_entries=FakeConfigEntries())
        old_watch_id = "private-entry-previous-id"
        key = bytes(range(16))
        entry = FakeEntry(version=2, data={"watches": [
            {"id": old_watch_id, "name": "Watch A", "irk": key.hex()},
            {"id": "independent-id", "name": "Watch B", "irk": key.hex()},
        ]})
        self.assertTrue(await integration.async_setup_entry(hass, entry))
        self.assertEqual(
            [watch.private_entry_id for watch in entry.runtime_data.watches],
            [old_watch_id, "independent-id"],
        )
        self.assertEqual(entry.runtime_data.watches[0].irk, key)

    async def test_unknown_future_config_version_is_rejected(self):
        integration, _ = load_integration()
        hass = types.SimpleNamespace(config_entries=FakeConfigEntries())
        entry = FakeEntry(version=3)
        self.assertFalse(await integration.async_migrate_entry(hass, entry))


if __name__ == "__main__":
    unittest.main()

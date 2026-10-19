"""Protect configured v2 Watch identities when updating to v1.2."""

import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

COMPONENT = Path(__file__).resolve().parents[1] / "custom_components" / "watch_ble_presence"


def load_integration_and_entity():
    package_name = "watch_ble_12_test"
    package = types.ModuleType(package_name)
    package.__path__ = [str(COMPONENT)]

    const = types.ModuleType(package_name + ".const")
    const.CONF_WATCHES = "watches"
    const.PLATFORMS = ["binary_sensor", "sensor"]
    const.DOMAIN = "watch_ble_presence"

    coordinator = types.ModuleType(package_name + ".coordinator")

    class WatchDefinition:
        def __init__(self, watch_id, irk, name):
            self.watch_id = watch_id
            self.irk = irk
            self.name = name

    class WatchBleCoordinator:
        def __init__(self, hass, entry, watches):
            self.watches = watches
            self.hass = hass

        async def async_config_entry_first_refresh(self):
            pass

    coordinator.WatchDefinition = WatchDefinition
    coordinator.WatchBleCoordinator = WatchBleCoordinator
    coordinator.WatchState = object

    ha = types.ModuleType("homeassistant")
    ce = types.ModuleType("homeassistant.config_entries")
    ce.ConfigEntry = object
    core = types.ModuleType("homeassistant.core")
    core.HomeAssistant = object
    helpers = types.ModuleType("homeassistant.helpers")
    dr = types.ModuleType("homeassistant.helpers.device_registry")
    dr.DeviceInfo = lambda **kwargs: kwargs
    update = types.ModuleType("homeassistant.helpers.update_coordinator")

    class CoordinatorEntity:
        def __class_getitem__(cls, item):
            return cls

        def __init__(self, coordinator):
            self.coordinator = coordinator

    update.CoordinatorEntity = CoordinatorEntity
    helpers.device_registry = dr
    helpers.update_coordinator = update
    modules = {
        package_name: package,
        package_name + ".const": const,
        package_name + ".coordinator": coordinator,
        "homeassistant": ha,
        "homeassistant.config_entries": ce,
        "homeassistant.core": core,
        "homeassistant.helpers": helpers,
        "homeassistant.helpers.device_registry": dr,
        "homeassistant.helpers.update_coordinator": update,
    }

    with patch.dict(sys.modules, modules):
        def load(name, path, **kwargs):
            spec = importlib.util.spec_from_file_location(name, COMPONENT / path, **kwargs)
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)
            return module

        integration = load(
            package_name, "__init__.py",
            submodule_search_locations=[str(COMPONENT)],
        )
        entity = load(package_name + ".entity", "entity.py")

    return integration, entity


class FakeConfigEntries:
    def __init__(self):
        self.forwarded = []
        self.unloaded = []

    async def async_forward_entry_setups(self, entry, platforms):
        self.forwarded.append(entry)

    async def async_unload_platforms(self, entry, platforms):
        self.unloaded.append(entry)
        return True


class ExistingEntryTests(unittest.IsolatedAsyncioTestCase):
    async def test_existing_four_irks_ids_and_entity_identity(self):
        integration, entity_module = load_integration_and_entity()
        watch_ids = ["old-one", "old-two", "old-three", "old-four"]
        watches = [
            {"id": value, "name": f"Watch {idx}", "irk": bytes([idx] * 16).hex()}
            for idx, value in enumerate(watch_ids, 1)
        ]
        original = {"watches": watches}
        entry = types.SimpleNamespace(
            version=2,
            data={"watches": [dict(watch) for watch in watches]},
            options={"update_interval": 15, "presence_timeout": 300},
            runtime_data=None,
        )
        hass = types.SimpleNamespace(config_entries=FakeConfigEntries())

        self.assertFalse(hasattr(integration, "async_migrate_entry"))
        self.assertTrue(await integration.async_setup_entry(hass, entry))
        self.assertEqual(entry.data, original)
        self.assertEqual(
            [watch.watch_id for watch in entry.runtime_data.watches], watch_ids
        )
        self.assertEqual(entry.options["update_interval"], 15)

        # The entity's registry key must remain exactly as in previous versions.
        for watch in entry.runtime_data.watches:
            entity = entity_module.WatchBleEntity(entry.runtime_data, watch, "detected")
            self.assertEqual(entity._attr_unique_id, watch.watch_id + "_detected")
            self.assertEqual(
                entity._attr_device_info["identifiers"],
                {("watch_ble_presence", watch.watch_id)},
            )

        self.assertTrue(await integration.async_unload_entry(hass, entry))
        self.assertEqual(hass.config_entries.unloaded, [entry])

    async def test_empty_independent_entry_is_valid(self):
        integration, _ = load_integration_and_entity()
        entry = types.SimpleNamespace(data={"watches": []}, options={})
        hass = types.SimpleNamespace(config_entries=FakeConfigEntries())
        self.assertTrue(await integration.async_setup_entry(hass, entry))
        self.assertEqual(entry.runtime_data.watches, [])


if __name__ == "__main__":
    unittest.main()

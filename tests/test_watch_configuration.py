"""Tests for reusing a Watch's existing entity identity when adding its IRK."""

import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

COMPONENT = Path(__file__).resolve().parents[1] / "custom_components" / "watch_ble_presence"


def load_config_flow():
    """Load config flow with small API stubs instead of the full HA runtime."""
    prefix = "watch_ble_config_flow_test"
    package = types.ModuleType(prefix)
    package.__path__ = [str(COMPONENT)]
    const = types.ModuleType(prefix + ".const")
    for field, value in {
        "CONF_IRK": "irk", "CONF_NAME": "name", "CONF_PRESENCE_TIMEOUT": "presence_timeout",
        "CONF_UPDATE_INTERVAL": "update_interval", "CONF_WATCHES": "watches",
        "DEFAULT_PRESENCE_TIMEOUT": 300, "DEFAULT_UPDATE_INTERVAL": 60,
        "DOMAIN": "watch_ble_presence",
    }.items():
        setattr(const, field, value)
    irk = types.ModuleType(prefix + ".irk")
    irk.parse_irk = lambda key: bytes.fromhex(key) if len(key) == 32 else None
    vol = types.ModuleType("voluptuous")
    vol.Schema = lambda x: x
    vol.Required = lambda key, **kwargs: key
    vol.Optional = lambda key, **kwargs: key
    vol.In = lambda options: options
    vol.All = lambda *items: items
    vol.Coerce = lambda value: value
    vol.Range = lambda **kwargs: kwargs

    ha = types.ModuleType("homeassistant")
    ce = types.ModuleType("homeassistant.config_entries")
    class ConfigFlow:
        def __init_subclass__(cls, **kwargs):
            pass
    class OptionsFlowWithReload:
        def async_create_entry(self, *, data):
            return {"type": "create_entry", "data": data}
    ce.ConfigFlow = ConfigFlow
    ce.ConfigEntry = object
    ce.ConfigFlowResult = dict
    ce.OptionsFlowWithReload = OptionsFlowWithReload
    ha.config_entries = ce
    core = types.ModuleType("homeassistant.core")
    core.callback = lambda fn: fn
    helpers = types.ModuleType("homeassistant.helpers")
    registry = types.ModuleType("homeassistant.helpers.entity_registry")
    registry.async_get = lambda hass: hass.registry
    helpers.entity_registry = registry

    modules = {
        prefix: package,
        prefix + ".const": const,
        prefix + ".irk": irk,
        "voluptuous": vol,
        "homeassistant": ha,
        "homeassistant.config_entries": ce,
        "homeassistant.core": core,
        "homeassistant.helpers": helpers,
        "homeassistant.helpers.entity_registry": registry,
    }
    with patch.dict(sys.modules, modules):
        spec = importlib.util.spec_from_file_location(prefix + ".config_flow", COMPONENT / "config_flow.py")
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
    return mod


class FakeConfigEntries:
    def __init__(self):
        self.reloads = []

    def async_update_entry(self, entry, *, data):
        entry.data = data

    async def async_reload(self, entry_id):
        self.reloads.append(entry_id)


class WatchConfigurationTests(unittest.IsolatedAsyncioTestCase):
    async def test_select_old_watch_id_preserves_entity_unique_id(self):
        flow_module = load_config_flow()
        current_entry_id = "our-integration-entry"
        old_watch_id = "stable-watch-identifier"
        old_entity = types.SimpleNamespace(
            config_entry_id=current_entry_id,
            unique_id=old_watch_id + "_detected",
            name="Kitchen Watch",
            entity_id="binary_sensor.kitchen_watch_ble_detected",
        )
        other_integration = types.SimpleNamespace(
            config_entry_id="private-ble-other-integration",
            unique_id="other-secret-watch_detected",
            name="Not ours",
            entity_id="binary_sensor.other",
        )
        hass = types.SimpleNamespace(
            registry=types.SimpleNamespace(entities={"own": old_entity, "other": other_integration}),
            config_entries=FakeConfigEntries(),
        )
        entry = types.SimpleNamespace(entry_id=current_entry_id, data={"watches": []}, options={})
        self.assertEqual(list(flow_module.legacy_watch_ids(hass, entry)), [old_watch_id])

        flow = flow_module.WatchBlePresenceOptionsFlow()
        flow.hass = hass
        flow.config_entry = entry
        key = bytes(range(16)).hex()
        result = await flow.async_step_add_watch({
            "name": "Watch Paolo", "irk": key, "existing_watch": old_watch_id,
        })
        self.assertEqual(result["type"], "create_entry")
        self.assertEqual(entry.data["watches"][0]["id"], old_watch_id)
        self.assertEqual(entry.data["watches"][0]["irk"], key)
        self.assertEqual(hass.config_entries.reloads, [current_entry_id])


if __name__ == "__main__":
    unittest.main()

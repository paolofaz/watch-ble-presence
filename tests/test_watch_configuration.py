"""Tests for normal Watch configuration and stored ID preservation."""

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
        def async_show_form(self, *, step_id, data_schema, errors):
            return {"type": "form", "step_id": step_id, "errors": errors}
    ce.ConfigFlow = ConfigFlow
    ce.ConfigEntry = object
    ce.ConfigFlowResult = dict
    ce.OptionsFlowWithReload = OptionsFlowWithReload
    ha.config_entries = ce
    core = types.ModuleType("homeassistant.core")
    core.callback = lambda fn: fn
    helpers = types.ModuleType("homeassistant.helpers")

    modules = {
        prefix: package,
        prefix + ".const": const,
        prefix + ".irk": irk,
        "voluptuous": vol,
        "homeassistant": ha,
        "homeassistant.config_entries": ce,
        "homeassistant.core": core,
        "homeassistant.helpers": helpers,
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
    async def test_add_watch_keeps_existing_four_ids(self):
        flow_module = load_config_flow()
        old_ids = ["stable-1", "stable-2", "stable-3", "stable-4"]
        stored = [
            {"id": key, "name": f"Watch {i}", "irk": bytes([i] * 16).hex()}
            for i, key in enumerate(old_ids, 1)
        ]
        hass = types.SimpleNamespace(config_entries=FakeConfigEntries())
        entry = types.SimpleNamespace(
            entry_id="our-entry", data={"watches": stored},
            options={"update_interval": 15},
        )
        flow = flow_module.WatchBlePresenceOptionsFlow()
        flow.hass = hass
        flow.config_entry = entry

        added_irk = bytes([5] * 16).hex()
        result = await flow.async_step_add_watch({"name": "New Watch", "irk": added_irk})
        self.assertEqual(result["type"], "create_entry")
        self.assertEqual([w["id"] for w in entry.data["watches"][:4]], old_ids)
        self.assertEqual(
            [w["irk"] for w in entry.data["watches"][:4]],
            [w["irk"] for w in stored],
        )
        self.assertEqual(entry.data["watches"][4]["name"], "New Watch")
        self.assertEqual(entry.data["watches"][4]["irk"], added_irk)
        self.assertNotIn(entry.data["watches"][4]["id"], old_ids)
        self.assertEqual(entry.options, {"update_interval": 15})
        self.assertEqual(hass.config_entries.reloads, ["our-entry"])

    async def test_duplicate_irk_is_rejected(self):
        flow_module = load_config_flow()
        key = bytes(range(16)).hex()
        entry = types.SimpleNamespace(
            entry_id="entry",
            data={"watches": [{"id": "original", "name": "Watch", "irk": key}]},
            options={},
        )
        flow = flow_module.WatchBlePresenceOptionsFlow()
        flow.config_entry = entry
        flow.hass = types.SimpleNamespace(config_entries=FakeConfigEntries())
        result = await flow.async_step_add_watch({"name": "Duplicate", "irk": key})
        self.assertEqual(result["type"], "form")
        self.assertEqual(result["errors"], {"irk": "irk_already_configured"})
        self.assertEqual([w["id"] for w in entry.data["watches"]], ["original"])

    async def test_remove_keeps_other_id(self):
        flow_module = load_config_flow()
        key1 = bytes([1] * 16).hex()
        key2 = bytes([2] * 16).hex()
        entry = types.SimpleNamespace(
            entry_id="entry",
            data={"watches": [
                {"id": "keep", "name": "Watch 1", "irk": key1},
                {"id": "remove", "name": "Watch 2", "irk": key2},
            ]},
            options={},
        )
        hass = types.SimpleNamespace(config_entries=FakeConfigEntries())
        flow = flow_module.WatchBlePresenceOptionsFlow()
        flow.hass = hass
        flow.config_entry = entry
        result = await flow.async_step_remove_watch({"watch": "remove"})
        self.assertEqual(result["type"], "create_entry")
        self.assertEqual(
            entry.data["watches"],
            [{"id": "keep", "name": "Watch 1", "irk": key1}],
        )
        self.assertEqual(hass.config_entries.reloads, ["entry"])


if __name__ == "__main__":
    unittest.main()

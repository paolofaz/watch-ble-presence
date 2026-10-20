"""Verify resolver behavior with stubbed public Bluetooth APIs."""

import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

PATH = Path(__file__).resolve().parents[1] / "custom_components" / "watch_ble_presence" / "ble_resolver.py"


def load_resolver(ads):
    tools = types.ModuleType("bluetooth_data_tools")
    tools.get_cipher_for_irk = lambda irk: irk
    tools.resolve_private_address = lambda cipher, address: address.startswith(cipher.hex()[:2])
    hass = types.ModuleType("homeassistant")
    components = types.ModuleType("homeassistant.components")
    bluetooth = types.ModuleType("homeassistant.components.bluetooth")
    bluetooth.async_discovered_service_info = lambda _hass, _connectable: ads
    core = types.ModuleType("homeassistant.core")
    core.HomeAssistant = object
    components.bluetooth = bluetooth
    hass.components = components
    hass.core = core
    modules = {"bluetooth_data_tools": tools, "homeassistant": hass, "homeassistant.components": components, "homeassistant.components.bluetooth": bluetooth, "homeassistant.core": core}
    with patch.dict(sys.modules, modules):
        spec = importlib.util.spec_from_file_location("ble_resolver_test", PATH)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    return module.async_last_service_info


class ResolverTests(unittest.TestCase):
    def test_selects_newest_matching_address(self):
        ads = [types.SimpleNamespace(address="00:AA", time=12), types.SimpleNamespace(address="ff:BB", time=999), types.SimpleNamespace(address="00:CC", time=17)]
        self.assertEqual(load_resolver(ads)(object(), bytes(16)), ads[2])

    def test_no_match(self):
        ads = [types.SimpleNamespace(address="aa:BB", time=12)]
        self.assertIsNone(load_resolver(ads)(object(), bytes(16)))


if __name__ == "__main__":
    unittest.main()

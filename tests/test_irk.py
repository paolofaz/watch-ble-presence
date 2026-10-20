"""Lightweight IRK parser tests (no Home Assistant runtime needed)."""

import base64
import importlib.util
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1] / "custom_components" / "watch_ble_presence" / "irk.py"
spec = importlib.util.spec_from_file_location("irk_helper", PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
parse_irk = module.parse_irk


class ParseIrkTests(unittest.TestCase):
    def test_hex(self):
        key = bytes(range(16))
        self.assertEqual(parse_irk(key.hex()), key)
        self.assertEqual(parse_irk("irk:" + key.hex()), key)

    def test_base64(self):
        key = bytes(range(16))
        encoded = base64.b64encode(bytes(reversed(key))).decode()
        self.assertEqual(parse_irk(encoded), key)

    def test_invalid(self):
        for raw in ("", "00", "not-a-key", "ab" * 17, "a" * 32 + "zz"):
            with self.subTest(value=raw):
                self.assertIsNone(parse_irk(raw))


if __name__ == "__main__":
    unittest.main()

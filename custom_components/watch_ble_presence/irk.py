"""Normalize a BLE identity resolving key."""

import base64
import binascii


def parse_irk(value: str) -> bytes | None:
    """Return 16-byte IRK decoded from hex or Home Assistant base64 format."""
    value = value.strip().removeprefix("irk:")
    try:
        if value.endswith("="):
            key = bytes(reversed(base64.b64decode(value, validate=True)))
        else:
            key = bytes.fromhex(value)
    except (ValueError, binascii.Error):
        return None
    return key if len(key) == 16 else None

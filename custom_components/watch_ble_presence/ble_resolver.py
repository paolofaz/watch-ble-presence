"""Resolve watches from Home Assistant's Bluetooth advertisement cache."""

from bluetooth_data_tools import get_cipher_for_irk, resolve_private_address
from homeassistant.components import bluetooth
from homeassistant.core import HomeAssistant


def async_last_service_info(hass: HomeAssistant, irk: bytes):
    """Return newest discovered advertisement matching this watch IRK."""
    cipher = get_cipher_for_irk(irk)
    newest = None
    for info in bluetooth.async_discovered_service_info(hass, False):
        if resolve_private_address(cipher, info.address):
            if newest is None or newest.time < info.time:
                newest = info
    return newest

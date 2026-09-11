"""Constants for Watch BLE Presence."""

from homeassistant.const import Platform

DOMAIN = "watch_ble_presence"
PRIVATE_BLE_DOMAIN = "private_ble_device"

PLATFORMS = [Platform.BINARY_SENSOR, Platform.SENSOR]

CONF_UPDATE_INTERVAL = "update_interval"
CONF_PRESENCE_TIMEOUT = "presence_timeout"

DEFAULT_UPDATE_INTERVAL = 60
DEFAULT_PRESENCE_TIMEOUT = 300

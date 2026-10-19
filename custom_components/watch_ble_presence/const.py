"""Constants for Watch BLE Presence."""

from homeassistant.const import Platform

DOMAIN = "watch_ble_presence"
PLATFORMS = [Platform.BINARY_SENSOR, Platform.SENSOR]
CONF_WATCHES = "watches"
CONF_IRK = "irk"
CONF_NAME = "name"
CONF_WATCH_ID = "id"
CONF_UPDATE_INTERVAL = "update_interval"
CONF_PRESENCE_TIMEOUT = "presence_timeout"
DEFAULT_UPDATE_INTERVAL = 60
DEFAULT_PRESENCE_TIMEOUT = 300

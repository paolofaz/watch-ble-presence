"""Config flow for Watch BLE Presence."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry, ConfigFlowResult, OptionsFlowWithReload
from homeassistant.core import callback

from .const import (
    CONF_PRESENCE_TIMEOUT,
    CONF_UPDATE_INTERVAL,
    DEFAULT_PRESENCE_TIMEOUT,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    PRIVATE_BLE_DOMAIN,
)


class WatchBlePresenceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Watch BLE Presence."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Set up Watch BLE Presence."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if not any(
            entry.data.get("irk")
            for entry in self.hass.config_entries.async_entries(PRIVATE_BLE_DOMAIN)
        ):
            return self.async_abort(reason="no_private_ble_devices")

        if user_input is not None:
            return self.async_create_entry(title="Watch BLE Presence", data={})

        return self.async_show_form(step_id="user", data_schema=vol.Schema({}))

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry):
        """Return the options flow."""
        return WatchBlePresenceOptionsFlow()


class WatchBlePresenceOptionsFlow(OptionsFlowWithReload):
    """Manage Watch BLE Presence options."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage options."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        schema = vol.Schema(
            {
                vol.Required(CONF_UPDATE_INTERVAL): vol.All(
                    vol.Coerce(int), vol.Range(min=10, max=300)
                ),
                vol.Required(CONF_PRESENCE_TIMEOUT): vol.All(
                    vol.Coerce(int), vol.Range(min=60, max=3600)
                ),
            }
        )

        suggested = {
            CONF_UPDATE_INTERVAL: self.config_entry.options.get(
                CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
            ),
            CONF_PRESENCE_TIMEOUT: self.config_entry.options.get(
                CONF_PRESENCE_TIMEOUT, DEFAULT_PRESENCE_TIMEOUT
            ),
        }

        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(schema, suggested),
        )

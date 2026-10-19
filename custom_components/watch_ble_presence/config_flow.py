"""Config flow for Watch BLE Presence."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry, ConfigFlowResult, OptionsFlowWithReload
from homeassistant.core import callback
from homeassistant.helpers import entity_registry as er

from .const import (
    CONF_IRK,
    CONF_NAME,
    CONF_PRESENCE_TIMEOUT,
    CONF_UPDATE_INTERVAL,
    CONF_WATCHES,
    DEFAULT_PRESENCE_TIMEOUT,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
)
from .irk import parse_irk


def watch_schema(legacy_ids: dict[str, str] | None = None) -> vol.Schema:
    fields = {
        vol.Required(CONF_NAME): str,
        vol.Required(CONF_IRK): str,
    }
    if legacy_ids:
        fields[vol.Optional("existing_watch", default="new")] = vol.In(
            {"new": "New watch", **legacy_ids}
        )
    return vol.Schema(fields)


def legacy_watch_ids(hass, entry: ConfigEntry) -> dict[str, str]:
    """Find identifiers belonging to our own previously created entities."""
    ids = {}
    registry = er.async_get(hass)
    for entity in registry.entities.values():
        if entity.config_entry_id != entry.entry_id or not entity.unique_id.endswith("_detected"):
            continue
        identifier = entity.unique_id.removesuffix("_detected")
        ids[identifier] = entity.name or entity.entity_id
    return ids


class WatchBlePresenceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Configure a standalone Watch BLE Presence integration."""

    VERSION = 2

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
        errors = {}
        if user_input is not None:
            irk = parse_irk(user_input[CONF_IRK])
            if irk is None:
                errors[CONF_IRK] = "irk_not_valid"
            else:
                return self.async_create_entry(
                    title="Watch BLE Presence",
                    data={CONF_WATCHES: [{"id": uuid4().hex, "name": user_input[CONF_NAME].strip(), "irk": irk.hex()}]},
                )
        return self.async_show_form(step_id="user", data_schema=watch_schema(), errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry):
        return WatchBlePresenceOptionsFlow()


class WatchBlePresenceOptionsFlow(OptionsFlowWithReload):
    """Manage watched devices and timeouts."""

    async def async_step_init(self, user_input=None) -> ConfigFlowResult:
        return self.async_show_menu(step_id="init", menu_options=["settings", "add_watch", "remove_watch"])

    async def async_step_settings(self, user_input=None) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(data={**self.config_entry.options, **user_input})
        schema = vol.Schema({
            vol.Required(CONF_UPDATE_INTERVAL, default=self.config_entry.options.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)): vol.All(vol.Coerce(int), vol.Range(min=10, max=300)),
            vol.Required(CONF_PRESENCE_TIMEOUT, default=self.config_entry.options.get(CONF_PRESENCE_TIMEOUT, DEFAULT_PRESENCE_TIMEOUT)): vol.All(vol.Coerce(int), vol.Range(min=60, max=3600)),
        })
        return self.async_show_form(step_id="settings", data_schema=schema)

    async def async_step_add_watch(self, user_input=None) -> ConfigFlowResult:
        watches = list(self.config_entry.data.get(CONF_WATCHES, []))
        used = {watch["id"] for watch in watches}
        old_ids = {key: val for key, val in legacy_watch_ids(self.hass, self.config_entry).items() if key not in used}
        errors = {}
        if user_input is not None:
            irk = parse_irk(user_input[CONF_IRK])
            if irk is None:
                errors[CONF_IRK] = "irk_not_valid"
            elif any(w["irk"] == irk.hex() for w in watches):
                errors[CONF_IRK] = "irk_already_configured"
            elif not user_input[CONF_NAME].strip():
                errors[CONF_NAME] = "name_required"
            else:
                chosen = user_input.get("existing_watch", "new")
                watch_id = chosen if chosen in old_ids else uuid4().hex
                watches.append({"id": watch_id, "name": user_input[CONF_NAME].strip(), "irk": irk.hex()})
                self.hass.config_entries.async_update_entry(self.config_entry, data={**self.config_entry.data, CONF_WATCHES: watches})
                await self.hass.config_entries.async_reload(self.config_entry.entry_id)
                return self.async_create_entry(data=dict(self.config_entry.options))
        return self.async_show_form(step_id="add_watch", data_schema=watch_schema(old_ids), errors=errors)

    async def async_step_remove_watch(self, user_input=None) -> ConfigFlowResult:
        watches = list(self.config_entry.data.get(CONF_WATCHES, []))
        if not watches:
            return self.async_abort(reason="no_watches")
        if user_input is not None:
            remaining = [watch for watch in watches if watch["id"] != user_input["watch"]]
            self.hass.config_entries.async_update_entry(self.config_entry, data={**self.config_entry.data, CONF_WATCHES: remaining})
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            return self.async_create_entry(data=dict(self.config_entry.options))
        return self.async_show_form(step_id="remove_watch", data_schema=vol.Schema({vol.Required("watch"): vol.In({w["id"]: w["name"] for w in watches})}))

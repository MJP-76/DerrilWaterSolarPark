"""Config flow for Kirk Hill Wind Farm SCADA Simulator."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_SCAN_INTERVAL,
    CONF_SITE_NAME,
    CONF_TURBINE_COUNT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SITE_NAME,
    DEFAULT_TURBINE_COUNT,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MAX_TURBINE_COUNT,
    MIN_SCAN_INTERVAL,
    MIN_TURBINE_COUNT,
)


def _user_schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Required(
                CONF_SITE_NAME, default=defaults.get(CONF_SITE_NAME, DEFAULT_SITE_NAME)
            ): str,
            vol.Required(
                CONF_TURBINE_COUNT,
                default=defaults.get(CONF_TURBINE_COUNT, DEFAULT_TURBINE_COUNT),
            ): vol.All(int, vol.Range(min=MIN_TURBINE_COUNT, max=MAX_TURBINE_COUNT)),
            vol.Required(
                CONF_SCAN_INTERVAL,
                default=defaults.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
            ): vol.All(int, vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL)),
        }
    )


class KirkhillCoopConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for the Kirk Hill Wind Farm SCADA Simulator."""

    VERSION = 2

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial setup step: site name, turbine count, scan interval."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        errors: dict[str, str] = {}

        if user_input is not None:
            return self.async_create_entry(
                title=user_input[CONF_SITE_NAME],
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=_user_schema(),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> KirkhillCoopOptionsFlow:
        """Return the options flow for this integration."""
        return KirkhillCoopOptionsFlow(config_entry)


class KirkhillCoopOptionsFlow(config_entries.OptionsFlow):
    """Handle options updates (turbine count / scan interval) after setup."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options: scan interval and turbine count."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = {**self._config_entry.data, **self._config_entry.options}

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_TURBINE_COUNT,
                    default=current.get(CONF_TURBINE_COUNT, DEFAULT_TURBINE_COUNT),
                ): vol.All(
                    int, vol.Range(min=MIN_TURBINE_COUNT, max=MAX_TURBINE_COUNT)
                ),
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=current.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                ): vol.All(
                    int, vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL)
                ),
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)

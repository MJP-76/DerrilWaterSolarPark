"""Config flow for the Derril Water Solar Park integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import CONF_API_KEY, CONF_SITE_NAME, DEFAULT_NAME, DOMAIN


class DerrilWaterSolarParkConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Derril Water Solar Park."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial setup step."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            return self.async_create_entry(
                title=user_input.get(CONF_SITE_NAME, DEFAULT_NAME),
                data={
                    CONF_API_KEY: user_input[CONF_API_KEY],
                    CONF_SITE_NAME: user_input.get(CONF_SITE_NAME, DEFAULT_NAME),
                },
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_KEY): str,
                    vol.Optional(CONF_SITE_NAME, default=DEFAULT_NAME): str,
                }
            ),
        )

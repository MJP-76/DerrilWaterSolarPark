"""Config flow for Kirk Hill Wind Farm integration."""
from __future__ import annotations

from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, DEFAULT_NAME, CONF_API_KEY


class KirkhillCoopConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Kirk Hill Wind Farm."""

    VERSION = 2

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the step where the user enters their credentials."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        errors: dict[str, str] = {}

        if user_input is not None:
            return self.async_create_entry(
                title=DEFAULT_NAME,
                data={CONF_API_KEY: user_input[CONF_API_KEY]},
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_API_KEY): str}),
            errors=errors,
        )

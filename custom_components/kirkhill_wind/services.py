"""Services for the Kirk Hill Wind Farm SCADA Simulator."""
from __future__ import annotations

import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall
import homeassistant.helpers.config_validation as cv

from .const import (
    ATTR_TURBINE_ID,
    ATTR_WIND_SPEED,
    DOMAIN,
    SERVICE_INJECT_FAULT,
    SERVICE_RESET_TURBINE,
    SERVICE_SET_WIND_SPEED,
)

INJECT_FAULT_SCHEMA = vol.Schema({vol.Required(ATTR_TURBINE_ID): cv.positive_int})
RESET_TURBINE_SCHEMA = vol.Schema({vol.Required(ATTR_TURBINE_ID): cv.positive_int})
SET_WIND_SPEED_SCHEMA = vol.Schema(
    {vol.Required(ATTR_WIND_SPEED): vol.All(vol.Coerce(float), vol.Range(min=0, max=25))}
)


def _all_coordinators(hass: HomeAssistant):
    """Yield the coordinator for every configured entry of this domain."""
    for entry in hass.config_entries.async_entries(DOMAIN):
        coordinator = getattr(entry, "runtime_data", None)
        if coordinator is not None:
            yield coordinator


async def async_setup_services(hass: HomeAssistant) -> None:
    """Register the kirkhill_wind services (idempotent)."""

    async def handle_inject_fault(call: ServiceCall) -> None:
        turbine_id = call.data[ATTR_TURBINE_ID]
        for coordinator in _all_coordinators(hass):
            if coordinator.inject_fault(turbine_id):
                await coordinator.async_request_refresh()

    async def handle_reset_turbine(call: ServiceCall) -> None:
        turbine_id = call.data[ATTR_TURBINE_ID]
        for coordinator in _all_coordinators(hass):
            if coordinator.reset_turbine(turbine_id):
                await coordinator.async_request_refresh()

    async def handle_set_wind_speed(call: ServiceCall) -> None:
        wind_speed = call.data[ATTR_WIND_SPEED]
        for coordinator in _all_coordinators(hass):
            coordinator.set_wind_speed(wind_speed)
            await coordinator.async_request_refresh()

    if not hass.services.has_service(DOMAIN, SERVICE_INJECT_FAULT):
        hass.services.async_register(
            DOMAIN, SERVICE_INJECT_FAULT, handle_inject_fault, schema=INJECT_FAULT_SCHEMA
        )
    if not hass.services.has_service(DOMAIN, SERVICE_RESET_TURBINE):
        hass.services.async_register(
            DOMAIN, SERVICE_RESET_TURBINE, handle_reset_turbine, schema=RESET_TURBINE_SCHEMA
        )
    if not hass.services.has_service(DOMAIN, SERVICE_SET_WIND_SPEED):
        hass.services.async_register(
            DOMAIN,
            SERVICE_SET_WIND_SPEED,
            handle_set_wind_speed,
            schema=SET_WIND_SPEED_SCHEMA,
        )


async def async_unload_services(hass: HomeAssistant) -> None:
    """Remove services once the last config entry is unloaded."""
    if hass.config_entries.async_entries(DOMAIN):
        return

    for service in (SERVICE_INJECT_FAULT, SERVICE_RESET_TURBINE, SERVICE_SET_WIND_SPEED):
        if hass.services.has_service(DOMAIN, service):
            hass.services.async_remove(DOMAIN, service)

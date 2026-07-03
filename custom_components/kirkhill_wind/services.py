"""Services for the Kirk Hill Wind Farm integration.

The simulator-era inject_fault / reset_turbine / set_wind_speed services are
no longer applicable now that the integration uses real API data. This module
is retained as a no-op stub so __init__.py can import it without changes if
custom services are added in future.
"""
from __future__ import annotations

from homeassistant.core import HomeAssistant


async def async_setup_services(hass: HomeAssistant) -> None:  # noqa: ARG001
    """Register domain services (none currently)."""


async def async_unload_services(hass: HomeAssistant) -> None:  # noqa: ARG001
    """Unload domain services (none currently)."""

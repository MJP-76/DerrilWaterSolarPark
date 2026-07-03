"""Sensor platform for Derril Water Solar Park."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_SITE_NAME


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    """Set up starter sensors for a config entry."""
    async_add_entities([DerrilSolarIntegrationStatusSensor(entry)])


class DerrilSolarIntegrationStatusSensor(SensorEntity):
    """Starter status sensor for a freshly scaffolded integration."""

    _attr_name = "Integration status"
    _attr_icon = "mdi:solar-power"

    def __init__(self, entry: ConfigEntry) -> None:
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_integration_status"

    @property
    def native_value(self) -> str:
        return "configured"

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        return {
            "site_name": self._entry.data.get(CONF_SITE_NAME, ""),
            "project_type": "solar_farm_starter",
        }

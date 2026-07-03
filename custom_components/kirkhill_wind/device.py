"""Device info helpers for the Kirk Hill Wind Farm integration."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo

from .const import CONF_SITE_NAME, DEFAULT_SITE_NAME, DOMAIN


def get_farm_device_info(entry) -> DeviceInfo:
    """Device info for the wind farm hub (farm-level sensors)."""
    return DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=entry.data.get(CONF_SITE_NAME, DEFAULT_SITE_NAME),
        manufacturer="Kirk Hill Co-op",
        model="Wind Farm API",
        entry_type=DeviceEntryType.SERVICE,
    )


def get_turbine_device_info(entry, turbine_id: str) -> DeviceInfo:
    """Device info for an individual turbine (e.g. turbine_id='T1').

    Linked to the farm hub device via ``via_device``.
    """
    return DeviceInfo(
        identifiers={(DOMAIN, f"{entry.entry_id}_{turbine_id}")},
        name=f"Turbine {turbine_id}",
        manufacturer="Kirk Hill Co-op",
        model="Wind Turbine",
        via_device=(DOMAIN, entry.entry_id),
    )

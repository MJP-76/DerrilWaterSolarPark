from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo

from .const import DOMAIN


def get_farm_device_info(entry) -> DeviceInfo:
    """Device info for the overall wind farm SCADA hub."""
    return DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=entry.data.get("site_name", "Kirk Hill Wind Farm"),
        manufacturer="Kirk Hill Co-op",
        model="Wind Farm SCADA Simulator",
        entry_type=DeviceEntryType.SERVICE,
    )


def get_turbine_device_info(entry, turbine_id: int) -> DeviceInfo:
    """Device info for an individual turbine, linked to the farm hub device."""
    return DeviceInfo(
        identifiers={(DOMAIN, f"{entry.entry_id}_turbine_{turbine_id}")},
        name=f"Turbine T{turbine_id}",
        manufacturer="Kirk Hill Co-op",
        model="Simulated Wind Turbine",
        via_device=(DOMAIN, entry.entry_id),
    )


def get_device_info(entry, scope: str) -> DeviceInfo:
    """Legacy helper retained for backwards compatibility."""
    return DeviceInfo(
        identifiers={(DOMAIN, f"{entry.entry_id}_{scope}")},
        name=f"Kirk Hill {scope.capitalize()}",
        manufacturer="Kirk Hill Co-op",
        model="Wind Farm Data Feed",
        entry_type=DeviceEntryType.SERVICE,
    )

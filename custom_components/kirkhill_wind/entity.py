from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .device import get_farm_device_info, get_turbine_device_info


class KirkHillEntity(CoordinatorEntity, Entity):
    """Base entity for farm-level (hub) sensors."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, entry, unique_suffix: str):
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{unique_suffix}"

    @property
    def device_info(self) -> DeviceInfo:
        return get_farm_device_info(self._entry)

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success


class KirkHillTurbineEntity(CoordinatorEntity, Entity):
    """Base entity for per-turbine sensors, linked to the farm hub device."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, entry, turbine_index: int, unique_suffix: str):
        super().__init__(coordinator)
        self._entry = entry
        self._turbine_index = turbine_index
        self._attr_unique_id = (
            f"{entry.entry_id}_turbine_{turbine_index + 1}_{unique_suffix}"
        )

    @property
    def turbine_data(self) -> dict:
        return self.coordinator.data["turbines"][self._turbine_index]

    @property
    def device_info(self) -> DeviceInfo:
        return get_turbine_device_info(self._entry, self._turbine_index + 1)

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success

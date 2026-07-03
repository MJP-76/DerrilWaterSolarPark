"""Binary sensor platform for the Kirk Hill Wind Farm SCADA Simulator."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)

from .entity import KirkHillEntity, KirkHillTurbineEntity


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = entry.runtime_data

    entities = [FarmAlarmSensor(coordinator, entry)]

    for index in range(len(coordinator.turbines)):
        entities.append(TurbineFaultSensor(coordinator, entry, index))

    async_add_entities(entities)


class FarmAlarmSensor(KirkHillEntity, BinarySensorEntity):
    """On when the farm is in a degraded or critical state."""

    _attr_translation_key = "farm_alarm"
    _attr_name = "Alarm"
    _attr_device_class = BinarySensorDeviceClass.SAFETY

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "farm_alarm")

    @property
    def is_on(self) -> bool:
        return self.coordinator.data["farm"]["state"] in ("degraded", "critical")


class TurbineFaultSensor(KirkHillTurbineEntity, BinarySensorEntity):
    """On when a specific turbine is in a fault state."""

    _attr_translation_key = "turbine_fault"
    _attr_name = "Fault"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, coordinator, entry, index):
        super().__init__(coordinator, entry, index, "fault")

    @property
    def is_on(self) -> bool:
        return self.turbine_data["state"] == "fault"

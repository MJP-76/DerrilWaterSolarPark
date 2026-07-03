"""Sensor platform for the Kirk Hill Wind Farm SCADA Simulator."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfPower,
    UnitOfSpeed,
)

from .entity import KirkHillEntity, KirkHillTurbineEntity

FARM_STATE_ICONS = {
    "normal": "mdi:wind-turbine",
    "degraded": "mdi:wind-turbine-alert",
    "critical": "mdi:alert-octagon",
}

TURBINE_STATE_ICONS = {
    "normal": "mdi:wind-turbine",
    "fault": "mdi:wind-turbine-alert",
}


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = entry.runtime_data

    entities = [
        FarmPowerSensor(coordinator, entry),
        FarmWindSensor(coordinator, entry),
        FarmStateSensor(coordinator, entry),
        FarmFaultSensor(coordinator, entry),
        FarmCapacityFactorSensor(coordinator, entry),
    ]

    for index in range(len(coordinator.turbines)):
        entities.append(TurbinePowerSensor(coordinator, entry, index))
        entities.append(TurbineWindSensor(coordinator, entry, index))
        entities.append(TurbineHealthSensor(coordinator, entry, index))
        entities.append(TurbineStateSensor(coordinator, entry, index))

    async_add_entities(entities)


# ----------------------------
# FARM SENSORS
# ----------------------------

class FarmPowerSensor(KirkHillEntity, SensorEntity):
    _attr_translation_key = "farm_power"
    _attr_name = "Power output"
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.MEGA_WATT

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "farm_power")

    @property
    def native_value(self):
        return self.coordinator.data["farm"]["power_mw"]


class FarmWindSensor(KirkHillEntity, SensorEntity):
    _attr_translation_key = "farm_wind_speed"
    _attr_name = "Wind speed"
    _attr_device_class = SensorDeviceClass.WIND_SPEED
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfSpeed.METERS_PER_SECOND

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "farm_wind_speed")

    @property
    def native_value(self):
        return self.coordinator.data["farm"]["wind_speed"]


class FarmStateSensor(KirkHillEntity, SensorEntity):
    _attr_translation_key = "farm_state"
    _attr_name = "Farm state"
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = ["normal", "degraded", "critical"]

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "farm_state")

    @property
    def native_value(self):
        return self.coordinator.data["farm"]["state"]

    @property
    def icon(self):
        return FARM_STATE_ICONS.get(self.native_value, "mdi:wind-turbine")


class FarmFaultSensor(KirkHillEntity, SensorEntity):
    _attr_translation_key = "farm_faults"
    _attr_name = "Active faults"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:alert-circle"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "farm_faults")

    @property
    def native_value(self):
        return self.coordinator.data["farm"]["faults"]


class FarmCapacityFactorSensor(KirkHillEntity, SensorEntity):
    _attr_translation_key = "farm_capacity_factor"
    _attr_name = "Capacity factor"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_icon = "mdi:gauge"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "farm_capacity_factor")

    @property
    def native_value(self):
        return self.coordinator.data["farm"]["capacity_factor"]


# ----------------------------
# TURBINE SENSORS
# ----------------------------

class TurbinePowerSensor(KirkHillTurbineEntity, SensorEntity):
    _attr_translation_key = "turbine_power"
    _attr_name = "Power output"
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.MEGA_WATT

    def __init__(self, coordinator, entry, index):
        super().__init__(coordinator, entry, index, "power")

    @property
    def native_value(self):
        return self.turbine_data["power_mw"]


class TurbineWindSensor(KirkHillTurbineEntity, SensorEntity):
    _attr_translation_key = "turbine_wind_speed"
    _attr_name = "Wind speed"
    _attr_device_class = SensorDeviceClass.WIND_SPEED
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfSpeed.METERS_PER_SECOND

    def __init__(self, coordinator, entry, index):
        super().__init__(coordinator, entry, index, "wind_speed")

    @property
    def native_value(self):
        return self.turbine_data["wind_speed"]


class TurbineHealthSensor(KirkHillTurbineEntity, SensorEntity):
    _attr_translation_key = "turbine_health"
    _attr_name = "Health"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_icon = "mdi:heart-pulse"

    def __init__(self, coordinator, entry, index):
        super().__init__(coordinator, entry, index, "health")

    @property
    def native_value(self):
        return self.turbine_data["health"]


class TurbineStateSensor(KirkHillTurbineEntity, SensorEntity):
    _attr_translation_key = "turbine_state"
    _attr_name = "State"
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = ["normal", "fault"]

    def __init__(self, coordinator, entry, index):
        super().__init__(coordinator, entry, index, "state")

    @property
    def native_value(self):
        return self.turbine_data["state"]

    @property
    def icon(self):
        return TURBINE_STATE_ICONS.get(self.native_value, "mdi:wind-turbine")

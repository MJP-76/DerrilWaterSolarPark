"""Sensor platform for the Kirk Hill Wind Farm integration.

Farm-level sensors (attached to the farm hub device):
  - FarmPowerSensor(scope)           total_power_kw            owner + site
  - FarmCapacityFactorSensor(scope)  capacity_factor_percent   owner + site
  - FarmWindSpeedSensor              wind_speed_mps            single (scope-independent)
  - FarmActiveTurbinesSensor         active_turbines           single (physical)
  - FarmInactiveTurbinesSensor       inactive_turbines         single (physical)

Per-turbine sensors (attached to each turbine device):
  - TurbinePowerSensor(turbine_id, scope)          power_kw               owner + site
  - TurbineCapacityFactorSensor(turbine_id, scope) capacity_factor_pct    owner + site
  - TurbineWindSpeedSensor(turbine_id)             wind_speed_mps         single
  - TurbineStateSensor(turbine_id)                 state_text             single
"""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, UnitOfPower, UnitOfSpeed

from .const import SCOPE_OWNER, SCOPE_SITE, SCOPES
from .entity import (
    KirkHillEntity,
    KirkHillScopedEntity,
    KirkHillScopedTurbineEntity,
    KirkHillTurbineEntity,
)


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = entry.runtime_data

    # Discover turbine IDs from the first update (owner scope)
    turbine_ids = [
        t["id"] for t in coordinator.data[SCOPE_OWNER].get("turbines", [])
    ]

    entities: list = [
        # Farm: one sensor per scope for power and capacity factor
        *[FarmPowerSensor(coordinator, entry, scope) for scope in SCOPES],
        *[FarmCapacityFactorSensor(coordinator, entry, scope) for scope in SCOPES],
        # Farm: scope-independent sensors
        FarmWindSpeedSensor(coordinator, entry),
        FarmActiveTurbinesSensor(coordinator, entry),
        FarmInactiveTurbinesSensor(coordinator, entry),
    ]

    for tid in turbine_ids:
        entities += [
            TurbinePowerSensor(coordinator, entry, tid, scope)
            for scope in SCOPES
        ]
        entities += [
            TurbineCapacityFactorSensor(coordinator, entry, tid, scope)
            for scope in SCOPES
        ]
        entities.append(TurbineWindSpeedSensor(coordinator, entry, tid))
        entities.append(TurbineStateSensor(coordinator, entry, tid))

    async_add_entities(entities)


# ---------------------------------------------------------------------------
# FARM SENSORS
# ---------------------------------------------------------------------------

class FarmPowerSensor(KirkHillScopedEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.KILO_WATT

    def __init__(self, coordinator, entry, scope: str):
        super().__init__(coordinator, entry, scope, "farm_power")
        self._attr_name = f"Power ({scope})"

    @property
    def native_value(self):
        return self._scope_data()["summary"].get("total_power_kw")


class FarmCapacityFactorSensor(KirkHillScopedEntity, SensorEntity):
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_icon = "mdi:gauge"

    def __init__(self, coordinator, entry, scope: str):
        super().__init__(coordinator, entry, scope, "farm_capacity_factor")
        self._attr_name = f"Capacity factor ({scope})"

    @property
    def native_value(self):
        return self._scope_data()["summary"].get("capacity_factor_percent")


class FarmWindSpeedSensor(KirkHillEntity, SensorEntity):
    _attr_name = "Wind speed"
    _attr_device_class = SensorDeviceClass.WIND_SPEED
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfSpeed.METERS_PER_SECOND

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "farm_wind_speed")

    @property
    def native_value(self):
        # wind_speed_mps is the same for both scopes; use owner
        return self.coordinator.data[SCOPE_OWNER]["summary"].get("wind_speed_mps")


class FarmActiveTurbinesSensor(KirkHillEntity, SensorEntity):
    _attr_name = "Active turbines"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:wind-turbine"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "farm_active_turbines")

    @property
    def native_value(self):
        return self.coordinator.data[SCOPE_OWNER]["summary"].get("active_turbines")


class FarmInactiveTurbinesSensor(KirkHillEntity, SensorEntity):
    _attr_name = "Inactive turbines"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:wind-turbine-alert"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "farm_inactive_turbines")

    @property
    def native_value(self):
        return self.coordinator.data[SCOPE_OWNER]["summary"].get("inactive_turbines")


# ---------------------------------------------------------------------------
# TURBINE SENSORS
# ---------------------------------------------------------------------------

class TurbinePowerSensor(KirkHillScopedTurbineEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.KILO_WATT

    def __init__(self, coordinator, entry, turbine_id: str, scope: str):
        super().__init__(coordinator, entry, turbine_id, scope, "power")
        self._attr_name = f"Power ({scope})"

    @property
    def native_value(self):
        t = self._turbine_data(self._scope)
        return t.get("power_kw") if t else None


class TurbineCapacityFactorSensor(KirkHillScopedTurbineEntity, SensorEntity):
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_icon = "mdi:gauge"

    def __init__(self, coordinator, entry, turbine_id: str, scope: str):
        super().__init__(coordinator, entry, turbine_id, scope, "capacity_factor")
        self._attr_name = f"Capacity factor ({scope})"

    @property
    def native_value(self):
        t = self._turbine_data(self._scope)
        return t.get("capacity_factor_percent") if t else None


class TurbineWindSpeedSensor(KirkHillTurbineEntity, SensorEntity):
    _attr_name = "Wind speed"
    _attr_device_class = SensorDeviceClass.WIND_SPEED
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfSpeed.METERS_PER_SECOND

    def __init__(self, coordinator, entry, turbine_id: str):
        super().__init__(coordinator, entry, turbine_id, "wind_speed")

    @property
    def native_value(self):
        # wind_speed_mps is scope-independent; use owner scope
        t = self._turbine_data(SCOPE_OWNER)
        return t.get("wind_speed_mps") if t else None


class TurbineStateSensor(KirkHillTurbineEntity, SensorEntity):
    _attr_name = "State"
    _attr_icon = "mdi:information-outline"

    def __init__(self, coordinator, entry, turbine_id: str):
        super().__init__(coordinator, entry, turbine_id, "state_text")

    @property
    def native_value(self):
        t = self._turbine_data(SCOPE_OWNER)
        return t.get("state_text") if t else None

    @property
    def extra_state_attributes(self) -> dict:
        t = self._turbine_data(SCOPE_OWNER)
        if t is None:
            return {}
        return {
            "status": t.get("status"),
            "status_started_at": t.get("status_started_at"),
            "state_started_at": t.get("state_started_at"),
        }

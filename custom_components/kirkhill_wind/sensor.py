"""Sensor platform for the Kirk Hill Wind Farm integration."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, UnitOfEnergy, UnitOfPower, UnitOfSpeed

from .const import SCOPES, SCOPE_OWNER, TIMEFRAME_ORDER
from .entity import (
    KirkHillEntity,
    KirkHillScopedEntity,
    KirkHillScopedTurbineEntity,
    KirkHillTurbineEntity,
)

TIMEFRAME_LABELS = {
    "yesterday": "Generation (yesterday)",
    "today": "Generation (today)",
    "week": "Generation (week)",
    "month": "Generation (month)",
    "ytd": "Generation (ytd)",
    "year": "Generation (year)",
    "alltime": "Generation (alltime)",
}


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = entry.runtime_data

    turbine_ids = [t["id"] for t in coordinator.data[SCOPE_OWNER].get("turbines", [])]

    entities: list = [
        *[FarmPowerSensor(coordinator, entry, scope) for scope in SCOPES],
        *[FarmCapacityFactorSensor(coordinator, entry, scope) for scope in SCOPES],
        *[
            FarmGenerationByTimeframeSensor(coordinator, entry, scope, timeframe)
            for scope in SCOPES
            for timeframe in TIMEFRAME_ORDER
        ],
        FarmWindSpeedSensor(coordinator, entry),
        FarmActiveTurbinesSensor(coordinator, entry),
        FarmInactiveTurbinesSensor(coordinator, entry),
    ]

    for tid in turbine_ids:
        entities += [TurbinePowerSensor(coordinator, entry, tid, scope) for scope in SCOPES]
        entities += [
            TurbineCapacityFactorSensor(coordinator, entry, tid, scope) for scope in SCOPES
        ]
        entities.append(TurbineWindSpeedSensor(coordinator, entry, tid))
        entities.append(TurbineStateSensor(coordinator, entry, tid))

    async_add_entities(entities)


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


class FarmGenerationByTimeframeSensor(KirkHillScopedEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR

    def __init__(self, coordinator, entry, scope: str, timeframe: str):
        super().__init__(coordinator, entry, scope, f"farm_generation_{timeframe}")
        self._timeframe = timeframe
        self._attr_name = TIMEFRAME_LABELS.get(timeframe, f"Generation ({timeframe})")

    @property
    def native_value(self):
        summary = (
            self.coordinator.data.get("timeframe_summaries", {})
            .get(self._scope, {})
            .get(self._timeframe, {})
        )
        return summary.get("total_kwh")

    @property
    def extra_state_attributes(self) -> dict:
        attrs = super().extra_state_attributes
        attrs["timeframe"] = self._timeframe
        return attrs


class FarmWindSpeedSensor(KirkHillEntity, SensorEntity):
    _attr_name = "Wind speed"
    _attr_device_class = SensorDeviceClass.WIND_SPEED
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfSpeed.METERS_PER_SECOND

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "farm_wind_speed")

    @property
    def native_value(self):
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
        coords = self.coordinator.data.get("coordinates", {}).get(self._turbine_id, {})
        return {
            "status": t.get("status"),
            "status_started_at": t.get("status_started_at"),
            "state_started_at": t.get("state_started_at"),
            "latitude": coords.get("latitude"),
            "longitude": coords.get("longitude"),
            "location_source": coords.get("source"),
            "openstreetmap_node_id": coords.get("openstreetmap_node_id"),
        }

import logging
import random
from datetime import timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONF_SCAN_INTERVAL,
    CONF_TURBINE_COUNT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_TURBINE_COUNT,
    DOMAIN,
    RATED_POWER_MW,
)
from .simulator import TurbineSim

_LOGGER = logging.getLogger(__name__)


class KirkHillWindCoordinator(DataUpdateCoordinator):
    """SCADA simulator coordinator (control loop engine)."""

    def __init__(self, hass, entry):
        self.hass = hass
        self.entry = entry

        scan_interval = entry.options.get(
            CONF_SCAN_INTERVAL,
            entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )
        self.turbine_count = entry.options.get(
            CONF_TURBINE_COUNT,
            entry.data.get(CONF_TURBINE_COUNT, DEFAULT_TURBINE_COUNT),
        )

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )

        # ----------------------------
        # SCADA PLANT STATE
        # ----------------------------
        self.global_wind = 8.0
        self.turbines = [TurbineSim(i + 1) for i in range(self.turbine_count)]

    def apply_options(self):
        """Re-apply turbine count / scan interval after an options update."""
        scan_interval = self.entry.options.get(
            CONF_SCAN_INTERVAL,
            self.entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )
        self.update_interval = timedelta(seconds=scan_interval)

        new_count = self.entry.options.get(
            CONF_TURBINE_COUNT,
            self.entry.data.get(CONF_TURBINE_COUNT, DEFAULT_TURBINE_COUNT),
        )
        if new_count != self.turbine_count:
            if new_count > self.turbine_count:
                self.turbines.extend(
                    TurbineSim(i + 1)
                    for i in range(self.turbine_count, new_count)
                )
            else:
                self.turbines = self.turbines[:new_count]
            self.turbine_count = new_count

    def inject_fault(self, turbine_id: int):
        """Force a specific turbine into a fault state (used by service call)."""
        for t in self.turbines:
            if t.id == turbine_id:
                t.force_fault()
                return True
        return False

    def reset_turbine(self, turbine_id: int):
        """Reset a specific turbine back to normal, healthy operation."""
        for t in self.turbines:
            if t.id == turbine_id:
                t.reset()
                return True
        return False

    def set_wind_speed(self, wind_speed: float):
        """Override the global wind speed used by the simulation."""
        self.global_wind = max(0.0, min(25.0, wind_speed))

    async def _async_update_data(self):
        # ----------------------------
        # WIND FIELD DYNAMICS
        # ----------------------------
        self.global_wind += random.uniform(-0.3, 0.3)
        self.global_wind = max(0, min(25, self.global_wind))

        turbine_data = []
        faults = 0

        # ----------------------------
        # CONTROL LOOP EXECUTION
        # ----------------------------
        for t in self.turbines:
            snapshot = t.step(self.global_wind)
            turbine_data.append(snapshot)

            if snapshot["state"] == "fault":
                faults += 1

        # ----------------------------
        # FARM POWER
        # ----------------------------
        total_power = sum(t["power_mw"] for t in turbine_data)
        rated_capacity = len(self.turbines) * RATED_POWER_MW
        capacity_factor = (
            round((total_power / rated_capacity) * 100, 1)
            if rated_capacity
            else 0.0
        )

        # ----------------------------
        # FARM STATE ENGINE
        # ----------------------------
        if faults >= 2:
            farm_state = "critical"
        elif faults == 1:
            farm_state = "degraded"
        else:
            farm_state = "normal"

        # ----------------------------
        # RETURN SCADA DATA MODEL
        # ----------------------------
        return {
            "farm": {
                "power_mw": round(total_power, 2),
                "wind_speed": round(self.global_wind, 2),
                "state": farm_state,
                "faults": faults,
                "capacity_factor": capacity_factor,
            },
            "turbines": turbine_data,
        }

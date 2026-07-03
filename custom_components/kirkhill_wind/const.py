DOMAIN = "kirkhill_wind"

DEFAULT_NAME = "Kirk Hill Wind Farm"

CONF_API_KEY = "api_key"
CONF_SITE_NAME = "site_name"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_TURBINE_COUNT = "turbine_count"

DEFAULT_SITE_NAME = "Kirk Hill Wind Farm"
DEFAULT_SCAN_INTERVAL = 5  # SCADA tick (seconds)
DEFAULT_TURBINE_COUNT = 8

MIN_SCAN_INTERVAL = 1
MAX_SCAN_INTERVAL = 60
MIN_TURBINE_COUNT = 1
MAX_TURBINE_COUNT = 24

# Rated power per turbine (MW), used for capacity factor calculations.
RATED_POWER_MW = 11.25

PLATFORMS = ["sensor", "binary_sensor"]

# Service names
SERVICE_INJECT_FAULT = "inject_fault"
SERVICE_RESET_TURBINE = "reset_turbine"
SERVICE_SET_WIND_SPEED = "set_wind_speed"

ATTR_TURBINE_ID = "turbine_id"
ATTR_WIND_SPEED = "wind_speed"

# Backwards-compat alias (previous releases used this name directly).
TURBINE_COUNT = DEFAULT_TURBINE_COUNT

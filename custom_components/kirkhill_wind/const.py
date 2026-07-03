DOMAIN = "kirkhill_wind"

DEFAULT_NAME = "Kirk Hill Wind Farm"

# Configuration keys
CONF_API_KEY = "api_key"
CONF_BASE_URL = "base_url"
CONF_SITE_NAME = "site_name"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_BASE_URL = "https://dashboard.kirkhillcoop.org"
DEFAULT_SITE_NAME = "Kirk Hill Wind Farm"
DEFAULT_SCAN_INTERVAL = 60  # seconds between API polls

MIN_SCAN_INTERVAL = 30
MAX_SCAN_INTERVAL = 3600

# Generation scopes from the OpenAPI spec.
SCOPE_OWNER = "owner"
SCOPE_SITE = "site"
SCOPES = [SCOPE_OWNER, SCOPE_SITE]

PLATFORMS = ["sensor", "binary_sensor"]

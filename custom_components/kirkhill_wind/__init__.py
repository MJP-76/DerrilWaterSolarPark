"""The Kirk Hill Wind Farm integration."""
from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.components import frontend
from homeassistant.components.lovelace import (
    CONF_ICON,
    CONF_REQUIRE_ADMIN,
    CONF_SHOW_IN_SIDEBAR,
    CONF_TITLE,
    CONF_URL_PATH,
    LOVELACE_DATA,
)
from homeassistant.components.lovelace import dashboard as lovelace_dashboard
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import PLATFORMS
from .coordinator import KirkHillWindCoordinator
from .services import async_setup_services, async_unload_services

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Kirk Hill Wind Farm from a config entry."""
    coordinator = KirkHillWindCoordinator(hass, entry)

    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await async_setup_services(hass)

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await _async_ensure_dashboard(hass, entry)

    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Re-apply scan interval when options change."""
    coordinator: KirkHillWindCoordinator = entry.runtime_data
    coordinator.apply_options()
    await coordinator.async_request_refresh()


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        entry.runtime_data = None
        await async_unload_services(hass)

    return unload_ok


async def _async_ensure_dashboard(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Create and register a Lovelace dashboard tab for this integration."""
    if LOVELACE_DATA not in hass.data:
        _LOGGER.debug("Lovelace not loaded yet; skipping dashboard auto-create")
        return

    url_path = "kirk-hill-wind-dashboard"
    title = "Kirk Hill Wind Farm"
    icon = "mdi:wind-turbine"

    dashboards_collection = lovelace_dashboard.DashboardsCollection(hass)
    await dashboards_collection.async_load()

    item = next(
        (
            existing
            for existing in dashboards_collection.async_items()
            if existing.get(CONF_URL_PATH) == url_path
        ),
        None,
    )
    if item is None:
        try:
            item = await dashboards_collection.async_create_item(
                {
                    CONF_ICON: icon,
                    CONF_TITLE: title,
                    CONF_URL_PATH: url_path,
                    CONF_SHOW_IN_SIDEBAR: True,
                    CONF_REQUIRE_ADMIN: False,
                }
            )
        except (HomeAssistantError, vol.Invalid) as err:
            _LOGGER.warning("Failed to create Lovelace dashboard: %s", err)
            return

    lovelace_store = hass.data[LOVELACE_DATA].dashboards.get(url_path)
    if lovelace_store is None:
        lovelace_store = lovelace_dashboard.LovelaceStorage(hass, item)
        hass.data[LOVELACE_DATA].dashboards[url_path] = lovelace_store

    await lovelace_store.async_save(_build_dashboard_config())

    frontend.async_register_built_in_panel(
        hass,
        "lovelace",
        frontend_url_path=url_path,
        require_admin=item[CONF_REQUIRE_ADMIN],
        show_in_sidebar=item[CONF_SHOW_IN_SIDEBAR],
        sidebar_title=item[CONF_TITLE],
        sidebar_icon=item.get(CONF_ICON, icon),
        config={"mode": "storage"},
        update=True,
    )


def _build_dashboard_config() -> dict:
    """Generate the default storage dashboard config."""
    owner_generation_entities = [
        "sensor.kirk_hill_wind_farm_generation_yesterday_owner",
        "sensor.kirk_hill_wind_farm_generation_today_owner",
        "sensor.kirk_hill_wind_farm_generation_week_owner",
        "sensor.kirk_hill_wind_farm_generation_month_owner",
        "sensor.kirk_hill_wind_farm_generation_ytd_owner",
        "sensor.kirk_hill_wind_farm_generation_year_owner",
        "sensor.kirk_hill_wind_farm_generation_alltime_owner",
    ]
    site_generation_entities = [
        "sensor.kirk_hill_wind_farm_generation_yesterday_site",
        "sensor.kirk_hill_wind_farm_generation_today_site",
        "sensor.kirk_hill_wind_farm_generation_week_site",
        "sensor.kirk_hill_wind_farm_generation_month_site",
        "sensor.kirk_hill_wind_farm_generation_ytd_site",
        "sensor.kirk_hill_wind_farm_generation_year_site",
        "sensor.kirk_hill_wind_farm_generation_alltime_site",
    ]

    turbine_cards = []
    for i in range(1, 9):
        turbine_cards.append(
            {
                "type": "entities",
                "title": f"Turbine T{i}",
                "entities": [
                    f"sensor.turbine_t{i}_power_owner",
                    f"sensor.turbine_t{i}_power_site",
                    f"sensor.turbine_t{i}_capacity_factor_owner",
                    f"sensor.turbine_t{i}_capacity_factor_site",
                    f"sensor.turbine_t{i}_wind_speed",
                    f"sensor.turbine_t{i}_state",
                    f"binary_sensor.turbine_t{i}_active",
                ],
            }
        )

    return {
        "title": "Kirk Hill Wind Farm",
        "views": [
            {
                "title": "Overview",
                "path": "overview",
                "icon": "mdi:wind-turbine",
                "type": "sections",
                "max_columns": 2,
                "sections": [
                    {
                        "type": "grid",
                        "column_span": 2,
                        "cards": [
                            {
                                "type": "heading",
                                "heading": "Kirk Hill Wind Farm",
                                "heading_style": "title",
                                "icon": "mdi:wind-turbine",
                            }
                        ],
                    },
                    {
                        "type": "grid",
                        "cards": [
                            {
                                "type": "heading",
                                "heading": "Your share",
                                "heading_style": "title",
                            },
                            {
                                "type": "entities",
                                "title": "Owner metrics",
                                "show_header_toggle": False,
                                "entities": [
                                    "sensor.kirk_hill_wind_farm_power_owner",
                                    "sensor.kirk_hill_wind_farm_capacity_factor_owner",
                                    *owner_generation_entities,
                                ],
                            },
                            {
                                "type": "history-graph",
                                "title": "Owner and wind (last 6 hours)",
                                "hours_to_show": 6,
                                "entities": [
                                    "sensor.kirk_hill_wind_farm_power_owner",
                                    "sensor.kirk_hill_wind_farm_wind_speed",
                                ],
                            },
                            {
                                "type": "heading",
                                "heading": "Turbine map",
                                "heading_style": "title",
                            },
                            {
                                "type": "map",
                                "title": "",
                                "default_zoom": 15,
                                "theme_mode": "auto",
                                "entities": [
                                    f"sensor.turbine_t{i}_state" for i in range(1, 9)
                                ],
                            },
                        ],
                    },
                    {
                        "type": "grid",
                        "cards": [
                            {
                                "type": "heading",
                                "heading": "Whole site",
                                "heading_style": "title",
                            },
                            {
                                "type": "entities",
                                "title": "Site metrics",
                                "show_header_toggle": False,
                                "entities": [
                                    "sensor.kirk_hill_wind_farm_power_site",
                                    "sensor.kirk_hill_wind_farm_capacity_factor_site",
                                    "sensor.kirk_hill_wind_farm_wind_speed",
                                    "sensor.kirk_hill_wind_farm_active_turbines",
                                    "sensor.kirk_hill_wind_farm_inactive_turbines",
                                    "binary_sensor.kirk_hill_wind_farm_alarm",
                                    *site_generation_entities,
                                ],
                            },
                            {
                                "type": "history-graph",
                                "title": "Site and wind (last 6 hours)",
                                "hours_to_show": 6,
                                "entities": [
                                    "sensor.kirk_hill_wind_farm_power_site",
                                    "sensor.kirk_hill_wind_farm_wind_speed",
                                ],
                            },
                            {
                                "type": "heading",
                                "heading": "Turbine status",
                                "heading_style": "title",
                            },
                            {
                                "type": "grid",
                                "columns": 2,
                                "square": False,
                                "cards": [
                                    {
                                        "type": "tile",
                                        "entity": f"binary_sensor.turbine_t{i}_active",
                                        "name": f"T{i}",
                                    }
                                    for i in range(1, 9)
                                ],
                            },
                        ],
                    },
                ],
            },
            {
                "title": "Turbines",
                "path": "turbines",
                "icon": "mdi:wind-turbine",
                "cards": [
                    {
                        "type": "grid",
                        "columns": 2,
                        "square": False,
                        "cards": turbine_cards,
                    }
                ],
            },
        ],
    }

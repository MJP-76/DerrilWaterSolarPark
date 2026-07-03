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
from homeassistant.helpers import entity_registry as er

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
    await _async_ensure_dashboard(hass, entry)


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

    await lovelace_store.async_save(_build_dashboard_config(hass, entry))

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


def _entity_ids_for_entry(hass: HomeAssistant, entry: ConfigEntry) -> dict[str, str]:
    """Return a map of entity unique_id to current entity_id."""
    registry = er.async_get(hass)
    entity_ids: dict[str, str] = {}

    for entity_entry in er.async_entries_for_config_entry(registry, entry.entry_id):
        if entity_entry.unique_id:
            entity_ids[entity_entry.unique_id] = entity_entry.entity_id

    return entity_ids


def _build_dashboard_config(hass: HomeAssistant, entry: ConfigEntry) -> dict:
    """Generate the default storage dashboard config."""
    entity_ids = _entity_ids_for_entry(hass, entry)

    def farm_scoped(scope: str, suffix: str) -> str:
        return entity_ids[f"{entry.entry_id}_{scope}_{suffix}"]

    def farm(unique_suffix: str) -> str:
        return entity_ids[f"{entry.entry_id}_{unique_suffix}"]

    def turbine(turbine_id: str, unique_suffix: str) -> str:
        return entity_ids[f"{entry.entry_id}_turbine_{turbine_id}_{unique_suffix}"]

    owner_generation_entities = [
        farm_scoped("owner", "farm_generation_yesterday"),
        farm_scoped("owner", "farm_generation_today"),
        farm_scoped("owner", "farm_generation_week"),
        farm_scoped("owner", "farm_generation_month"),
        farm_scoped("owner", "farm_generation_ytd"),
        farm_scoped("owner", "farm_generation_year"),
        farm_scoped("owner", "farm_generation_alltime"),
    ]
    site_generation_entities = [
        farm_scoped("site", "farm_generation_yesterday"),
        farm_scoped("site", "farm_generation_today"),
        farm_scoped("site", "farm_generation_week"),
        farm_scoped("site", "farm_generation_month"),
        farm_scoped("site", "farm_generation_ytd"),
        farm_scoped("site", "farm_generation_year"),
        farm_scoped("site", "farm_generation_alltime"),
    ]

    turbine_cards = []
    for i in range(1, 9):
        turbine_id = f"T{i}"
        turbine_cards.append(
            {
                "type": "entities",
                "title": f"Turbine {turbine_id}",
                "entities": [
                    turbine(turbine_id, "owner_power"),
                    turbine(turbine_id, "site_power"),
                    turbine(turbine_id, "owner_capacity_factor"),
                    turbine(turbine_id, "site_capacity_factor"),
                    turbine(turbine_id, "wind_speed"),
                    turbine(turbine_id, "state_text"),
                    turbine(turbine_id, "active"),
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
                                    farm_scoped("owner", "farm_power"),
                                    farm_scoped("owner", "farm_capacity_factor"),
                                    *owner_generation_entities,
                                ],
                            },
                            {
                                "type": "history-graph",
                                "title": "Owner and wind (last 6 hours)",
                                "hours_to_show": 6,
                                "entities": [
                                    farm_scoped("owner", "farm_power"),
                                    farm("farm_wind_speed"),
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
                                    turbine(f"T{i}", "state_text") for i in range(1, 9)
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
                                    farm_scoped("site", "farm_power"),
                                    farm_scoped("site", "farm_capacity_factor"),
                                    farm("farm_wind_speed"),
                                    farm("farm_active_turbines"),
                                    farm("farm_inactive_turbines"),
                                    farm("farm_alarm"),
                                    *site_generation_entities,
                                ],
                            },
                            {
                                "type": "history-graph",
                                "title": "Site and wind (last 6 hours)",
                                "hours_to_show": 6,
                                "entities": [
                                    farm_scoped("site", "farm_power"),
                                    farm("farm_wind_speed"),
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
                                        "entity": turbine(f"T{i}", "active"),
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

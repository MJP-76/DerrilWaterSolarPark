"""Coordinator for the Kirk Hill Wind Farm integration.

Polls /api/v1/current for both owner and site scopes concurrently on each
update cycle and stores the combined result in coordinator.data.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import KirkHillApiClient
from .const import (
    CONF_API_KEY,
    CONF_BASE_URL,
    CONF_SCAN_INTERVAL,
    DEFAULT_BASE_URL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    SCOPE_OWNER,
    SCOPE_SITE,
)
from .exceptions import KirkHillApiError

_LOGGER = logging.getLogger(__name__)


class KirkHillWindCoordinator(DataUpdateCoordinator):
    """Fetches current data from both owner and site scopes on each tick."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        scan_interval = entry.options.get(
            CONF_SCAN_INTERVAL,
            entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.entry = entry
        self.client = KirkHillApiClient(
            api_key=entry.data[CONF_API_KEY],
            base_url=entry.data.get(CONF_BASE_URL, DEFAULT_BASE_URL),
        )

    def apply_options(self) -> None:
        """Re-apply scan interval when options change."""
        scan_interval = self.entry.options.get(
            CONF_SCAN_INTERVAL,
            self.entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )
        self.update_interval = timedelta(seconds=scan_interval)

    async def _async_update_data(self) -> dict:
        """Fetch current owner/site data and turbine coordinates."""
        async with aiohttp.ClientSession() as session:
            try:
                owner_data, site_data, site_turbines = await asyncio.gather(
                    self.client.get_current(session, SCOPE_OWNER),
                    self.client.get_current(session, SCOPE_SITE),
                    self.client.get_turbines(session, SCOPE_SITE),
                )
            except KirkHillApiError as exc:
                raise UpdateFailed(str(exc)) from exc

        coordinates: dict[str, dict[str, float | str | None]] = {}
        for row in site_turbines:
            turbine_id = row.get("id")
            coord = row.get("coordinates") or {}
            if turbine_id:
                coordinates[turbine_id] = {
                    "latitude": coord.get("latitude"),
                    "longitude": coord.get("longitude"),
                    "source": coord.get("source"),
                    "openstreetmap_node_id": coord.get("openstreetmap_node_id"),
                }

        return {
            SCOPE_OWNER: owner_data,
            SCOPE_SITE: site_data,
            "coordinates": coordinates,
        }

import asyncio
from datetime import timedelta
import logging

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import KirkHillWindApi
from .const import BASE_URL, DEFAULT_SCAN_INTERVAL, TIME_RANGES

_LOGGER = logging.getLogger(__name__)


class KirkHillWindCoordinator(DataUpdateCoordinator):
    """Kirk Hill Wind Farm coordinator."""

    def __init__(self, hass, entry):
        """Initialise coordinator."""
        self.hass = hass
        self.entry = entry

        self.api = KirkHillWindApi(
            base_url=BASE_URL,
            api_key=entry.data["api_key"],
        )

        super().__init__(
            hass,
            logger=_LOGGER,
            name="kirkhill_wind",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    @property
    def session(self):
        """Return shared aiohttp session."""
        return async_get_clientsession(self.hass)

    async def _async_update_data(self):
        """Fetch data from API."""
        try:
            session = self.session

            owner = await self._fetch_scope(session, "owner")
            site = await self._fetch_scope(session, "site")

            _LOGGER.debug("Owner data fetched successfully")
            _LOGGER.debug("Site data fetched successfully")

            data = {
                "owner": owner,
                "site": site,
            }
            
            _LOGGER.info("Coordinator data updated successfully")
            return data

        except Exception as err:
            _LOGGER.exception("Kirk Hill update failed")
            raise UpdateFailed(str(err)) from err

    async def _fetch_scope(self, session, scope: str):
        """Fetch all API endpoints for a scope."""
        try:
            summaries = await asyncio.gather(
                *[self.api.summary(session, scope, range_name=range_name) for range_name in TIME_RANGES]
            )
            summaries_by_range = {
                range_name: summary for range_name, summary in zip(TIME_RANGES, summaries)
            }

            generation, wind, turbines = await asyncio.gather(
                self.api.generation(session, scope),
                self.api.wind(session, scope),
                self.api.turbines(session, scope),
            )

            _LOGGER.debug(f"[{scope}] summary fetched")
            _LOGGER.debug(f"[{scope}] generation fetched")
            _LOGGER.debug(f"[{scope}] wind fetched")
            _LOGGER.debug(f"[{scope}] turbines fetched")

            return {
                "summary": summaries_by_range.get("today", {}),
                "summaries_by_range": summaries_by_range,
                "generation": generation,
                "wind": wind,
                "turbines": turbines,
            }
        except Exception as err:
            _LOGGER.error(f"Failed to fetch {scope} scope: {err}")
            raise

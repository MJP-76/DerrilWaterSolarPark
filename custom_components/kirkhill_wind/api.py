import logging

_LOGGER = logging.getLogger(__name__)


class KirkHillWindApiError(Exception):
    pass


class KirkHillWindApi:
    def __init__(self, base_url: str, api_key: str):
        self._base_url = base_url
        self._api_key = api_key

    async def request(self, session, path, params=None):
        url = f"{self._base_url}{path}"

        headers = {
            "Accept": "application/json",
        }
        headers["Authorization"] = "Bearer " + self._api_key

        try:
            _LOGGER.debug(f"API request to {url} with params {params}")
            async with session.get(url, headers=headers, params=params) as resp:
                _LOGGER.debug(f"API response status: {resp.status}")
                if resp.status >= 400:
                    error_text = await resp.text()
                    _LOGGER.error(f"API error {resp.status}: {error_text}")
                    raise KirkHillWindApiError(error_text)
                response = await resp.json()
                _LOGGER.debug("Raw API response received")
                # Extract the data field from the response
                extracted = response.get("data", response)
                _LOGGER.debug("Extracted data from response")
                return extracted
        except Exception as err:
            _LOGGER.error(f"API request failed: {err}", exc_info=True)
            raise

    async def summary(self, session, scope, range_name=None, year=None):
        params = {"scope": scope}
        if range_name:
            params["range"] = range_name
        if year is not None:
            params["year"] = str(year)
        return await self.request(session, "/api/v1/summary", params)

    async def generation(self, session, scope):
        return await self.request(session, "/api/v1/generation", {"scope": scope})

    async def wind(self, session, scope):
        return await self.request(session, "/api/v1/wind-speed", {"scope": scope})

    async def turbines(self, session, scope):
        return await self.request(session, "/api/v1/turbines", {"scope": scope})

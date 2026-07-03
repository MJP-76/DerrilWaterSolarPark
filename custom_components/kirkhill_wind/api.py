"""HTTP client for the Kirk Hill Wind Farm API."""
from __future__ import annotations

import asyncio
from typing import Any

import aiohttp

from .const import DEFAULT_BASE_URL, SCOPE_OWNER
from .exceptions import KirkHillAuthError, KirkHillConnectionError

TIMEOUT = aiohttp.ClientTimeout(total=20)


class KirkHillApiClient:
    """Async HTTP client aligned with the Kirk Hill Wind Farm OpenAPI spec."""

    def __init__(self, api_key: str, base_url: str = DEFAULT_BASE_URL) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": "Bearer " + self._api_key,
            "Accept": "application/json",
        }

    async def _get(
        self, session: aiohttp.ClientSession, path: str, params: dict[str, str]
    ) -> dict[str, Any]:
        url = f"{self._base_url}{path}"
        try:
            async with session.get(
                url, params=params, headers=self._headers, timeout=TIMEOUT
            ) as resp:
                if resp.status == 401:
                    raise KirkHillAuthError("Invalid or missing API key")
                resp.raise_for_status()
                return await resp.json()
        except KirkHillAuthError:
            raise
        except aiohttp.ClientError as exc:
            raise KirkHillConnectionError(str(exc)) from exc
        except asyncio.TimeoutError as exc:
            raise KirkHillConnectionError("Request timed out") from exc

    async def get_current(
        self, session: aiohttp.ClientSession, scope: str = SCOPE_OWNER
    ) -> dict[str, Any]:
        """GET /api/v1/current?scope={scope}."""
        body = await self._get(session, "/api/v1/current", {"scope": scope})
        return body["data"]

    async def get_turbines(
        self, session: aiohttp.ClientSession, scope: str = SCOPE_OWNER
    ) -> list[dict[str, Any]]:
        """GET /api/v1/turbines?scope={scope}."""
        body = await self._get(session, "/api/v1/turbines", {"scope": scope})
        return body["data"]["turbines"]

    async def get_summary(
        self,
        session: aiohttp.ClientSession,
        scope: str = SCOPE_OWNER,
        range_value: str = "today",
    ) -> dict[str, Any]:
        """GET /api/v1/summary?scope={scope}&range={range_value}."""
        body = await self._get(
            session,
            "/api/v1/summary",
            {"scope": scope, "range": range_value},
        )
        return body["data"]

    async def test(self, session: aiohttp.ClientSession) -> None:
        """Validate the API key by making a minimal current request."""
        await self.get_current(session, SCOPE_OWNER)

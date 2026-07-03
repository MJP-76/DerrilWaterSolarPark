"""HTTP client for the Kirk Hill Wind Farm API.

All endpoints are documented in openapi.yaml at the root of the repository.
Base URL: https://dashboard.kirkhillcoop.org
Auth:     Authorization: Bearer <api_key>
"""
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
            "Authorization": f"Bearer {self._api_key}",
            "Accept": "application/json",
        }

    async def get_current(
        self, session: aiohttp.ClientSession, scope: str = SCOPE_OWNER
    ) -> dict[str, Any]:
        """GET /api/v1/current?scope={scope}

        Returns data.reading, data.summary, data.turbines[] for the given scope.
        Wind speed in data.summary is scope-independent.
        """
        url = f"{self._base_url}/api/v1/current"
        try:
            async with session.get(
                url, params={"scope": scope}, headers=self._headers, timeout=TIMEOUT
            ) as resp:
                if resp.status == 401:
                    raise KirkHillAuthError("Invalid or missing API key")
                resp.raise_for_status()
                body = await resp.json()
                return body["data"]
        except KirkHillAuthError:
            raise
        except aiohttp.ClientError as exc:
            raise KirkHillConnectionError(str(exc)) from exc
        except asyncio.TimeoutError as exc:
            raise KirkHillConnectionError("Request timed out") from exc

    async def test(self, session: aiohttp.ClientSession) -> None:
        """Validate the API key by making a minimal current request."""
        await self.get_current(session, SCOPE_OWNER)

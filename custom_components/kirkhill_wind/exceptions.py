"""Exceptions for the Kirk Hill Wind Farm integration."""


class KirkHillApiError(Exception):
    """Base exception for all Kirk Hill API errors."""


class KirkHillAuthError(KirkHillApiError):
    """Raised when the API returns 401 Unauthorised."""


class KirkHillConnectionError(KirkHillApiError):
    """Raised when the API cannot be reached (network / timeout)."""

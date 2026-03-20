"""Provider-layer error types."""

from __future__ import annotations


class ProviderError(Exception):
    """Base class for provider-layer failures."""


class ProviderConfigurationError(ProviderError):
    """Raised when provider configuration is missing or invalid."""


class ProviderDataError(ProviderError):
    """Raised when provider data for a ticker is missing or malformed."""

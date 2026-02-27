

class ProviderError(Exception):
    """Catch-all for other API errors."""

    def __init__(self, message: str, provider: str, original_error: Exception | None = None) -> None:
        self.provider = provider
        self.original_error = original_error
        super().__init__(f"[{provider}] {message}")

class AuthenticationError(ProviderError):
    """API key is invalid or missing."""
    pass

class RateLimitExceededError(ProviderError):
    """Too many requests or quota exceeded."""
    pass

class ModelNotFoundError(ProviderError):
    """The requested model doesn't exist."""
    pass

class ConnectionError(ProviderError):
    """Can't reach the provider's API."""
    pass

class ProviderApiError(ProviderError):
    """Catch-all for other API errors."""
    pass
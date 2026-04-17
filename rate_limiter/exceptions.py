"""Custom exceptions for the rate limiter."""

class RateLimiterError(Exception):
    """Base exception for all rate limiter errors."""
    pass

class ConfigurationError(RateLimiterError):
    """Raised when the rate limiter is improperly configured."""
    pass

class RedisConnectionError(RateLimiterError):
    """Raised when there is an issue connecting to or communicating with Redis."""
    pass

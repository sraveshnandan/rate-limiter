"""Type definitions for the rate limiter."""

from dataclasses import dataclass
from typing import Callable, Any, Dict


@dataclass
class RateLimitResult:
    """Result of a rate limit check."""

    allowed: bool
    remaining: int
    retry_after: int
    limit: int
    window: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "allowed": self.allowed,
            "remaining": self.remaining,
            "retry_after": self.retry_after,
            "limit": self.limit,
            "window": self.window,
        }

    def to_http_headers(self) -> Dict[str, str]:
        """Convert to standard HTTP rate limit headers."""
        return {
            "retry-after": str(self.retry_after),
            "ratelimit-limit": str(self.limit),
            "ratelimit-remaining": str(self.remaining),
            "ratelimit-reset": str(self.retry_after),
        }


# Callable that takes a request-like object and returns a string key
KeyGenerator = Callable[[Any], str]
# Callable that takes a request-like object and returns a boolean (True to skip)
SkipCondition = Callable[[Any], bool]

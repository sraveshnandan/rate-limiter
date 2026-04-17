"""Rate Limiter for Python."""

from rate_limiter.core import RateLimiter
from rate_limiter.decorators import rate_limit, rate_limits

__version__ = "1.0.0"
__all__ = [
    "RateLimiter",
    "rate_limit",
    "rate_limits",
]

try:
    from rate_limiter.adapters.fastapi_adapter import RateLimiterMiddleware as FastAPIMiddleware
    __all__.append("FastAPIMiddleware")
except ImportError:
    pass

try:
    from rate_limiter.adapters.django_adapter import DjangoRateLimiter
    __all__.append("DjangoRateLimiter")
except ImportError:
    pass

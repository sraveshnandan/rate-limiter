"""Universal decorators for rate limiting."""
from rate_limiter.adapters.flask_adapter import rate_limit as flask_rate_limit
from rate_limiter.core import RateLimiter

# By default alias the Flask rate limiter to be the universal rate limiter 
# since FastAPI typically uses middleware, and Django uses middleware.
# (Additional logic could be added for async FastAPI decorators)

rate_limit = flask_rate_limit

# Alias multiple limits
def rate_limits(limiter: RateLimiter = None, **kwargs):
    """Alias for multiple limits."""
    return rate_limit(limiter, **kwargs)

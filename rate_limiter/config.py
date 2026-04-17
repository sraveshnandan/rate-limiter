"""Configuration structures for the rate limiter."""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from rate_limiter.types import KeyGenerator, SkipCondition
from rate_limiter.exceptions import ConfigurationError

@dataclass
class LimitTier:
    """Represents a single tiered limit (e.g., per minute or per hour)."""
    limit: int
    window: int  # in seconds
    scope: str = "global"

@dataclass
class RateLimiterConfig:
    """Main configuration for RateLimiter."""
    redis_url: Optional[str] = None
    redis_nodes: Optional[List[Dict[str, Any]]] = None
    limit: Optional[int] = None
    window: Optional[int] = None  # in seconds
    limits: Optional[List[LimitTier]] = None
    key_prefix: str = "rate_limit"
    key_generator: Optional[KeyGenerator] = None
    skip: Optional[SkipCondition] = None
    message: str = "Too Many Requests"
    error_message: str = "Rate limit exceeded"
    status_code: int = 429
    fail_open: bool = True  # If true, allow requests if Redis is down

    def __post_init__(self):
        """Validate configuration."""
        if not self.redis_url and not self.redis_nodes:
            raise ConfigurationError("Either redis_url or redis_nodes must be provided")
            
        if self.limit is None and self.window is None and not self.limits:
            raise ConfigurationError("Must provide either limit/window or a list of limits")
            
        if self.limit is not None and self.window is not None:
            if not self.limits:
                self.limits = [LimitTier(limit=self.limit, window=self.window, scope="default")]

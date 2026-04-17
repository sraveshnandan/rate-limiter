"""Core RateLimiter implementation."""
import time
from typing import Any, Optional
from rate_limiter.config import RateLimiterConfig
from rate_limiter.redis_client import RedisClientWrapper
from rate_limiter.types import RateLimitResult

class RateLimiter:
    def __init__(self, **kwargs):
        self.config = RateLimiterConfig(**kwargs)
        self.redis = RedisClientWrapper(
            redis_url=self.config.redis_url,
            redis_nodes=self.config.redis_nodes,
            fail_open=self.config.fail_open
        )

    def _generate_key(self, identifier: str, endpoint: str, scope: str) -> str:
        """Generate the Redis key for the rate limit."""
        return f"{self.config.key_prefix}:{scope}:{identifier}:{endpoint}"

    def check_rate_limit(self, identifier: str, endpoint: str) -> RateLimitResult:
        """
        Check rate limits against all configured tiers.
        """
        if not self.config.limits:
            return RateLimitResult(True, 1, 0, 1, 1)

        now_ms = int(time.time() * 1000)
        import uuid
        request_id = str(uuid.uuid4())
        
        # Track the minimum remaining and maximum retry_after across all tiers
        min_remaining = float('inf')
        max_retry_after = 0
        overall_allowed = True
        most_restrictive_limit = self.config.limits[0].limit
        most_restrictive_window = self.config.limits[0].window

        for tier in self.config.limits:
            key = self._generate_key(identifier, endpoint, tier.scope)
            window_ms = tier.window * 1000
            
            result = self.redis.execute_sliding_window(
                key=key,
                limit=tier.limit,
                window_ms=window_ms,
                now_ms=now_ms,
                request_id=request_id
            )

            # If Redis fails and we fail_open, allow the request
            if result is None:
                continue

            allowed_flag, remaining, retry_after = result
            allowed = bool(allowed_flag)
            
            if not allowed:
                overall_allowed = False
                
            if remaining < min_remaining:
                min_remaining = remaining
                most_restrictive_limit = tier.limit
                most_restrictive_window = tier.window
                
            if retry_after > max_retry_after:
                max_retry_after = retry_after
                most_restrictive_limit = tier.limit
                most_restrictive_window = tier.window

        if min_remaining == float('inf'):
            # Redis failed and fail_open is true
            min_remaining = most_restrictive_limit
            overall_allowed = True
            
        return RateLimitResult(
            allowed=overall_allowed,
            remaining=max(0, int(min_remaining)) if overall_allowed else 0,
            retry_after=max_retry_after,
            limit=most_restrictive_limit,
            window=most_restrictive_window
        )

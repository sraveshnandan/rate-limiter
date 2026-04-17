"""Redis client wrapper with connection pooling and script caching."""
import logging
from typing import List, Dict, Any, Optional, Tuple

import redis
from rate_limiter.exceptions import RedisConnectionError
from rate_limiter.lua_scripts import SLIDING_WINDOW_SCRIPT

logger = logging.getLogger("rate_limiter.redis")

class RedisClientWrapper:
    """Wraps the Redis connection to handle cluster/standalone and script loading."""
    
    def __init__(self, 
                 redis_url: Optional[str] = None, 
                 redis_nodes: Optional[List[Dict[str, Any]]] = None,
                 fail_open: bool = True):
        self.redis_url = redis_url
        self.redis_nodes = redis_nodes
        self.fail_open = fail_open
        self.client = None
        self._script_obj = None
        self._connect()
        
    def _connect(self):
        """Initialize the Redis connection pool."""
        try:
            if self.redis_nodes:
                # Handle Redis Cluster
                try:
                    from redis.cluster import RedisCluster
                    startup_nodes = [{"host": node["host"], "port": str(node.get("port", 6379))} 
                                     for node in self.redis_nodes]
                    # decode_responses=False to ensure compatibility with Lua script response format if needed
                    self.client = RedisCluster(startup_nodes=startup_nodes, decode_responses=False)
                except ImportError:
                    logger.warning("redis-cluster dependency not found. Falling back to primary node.")
                    first_node = self.redis_nodes[0]
                    self.client = redis.Redis(
                        host=first_node["host"], 
                        port=int(first_node.get("port", 6379)),
                        decode_responses=False
                    )
            elif self.redis_url:
                # Handle standalone Redis URL connection pooling
                pool = redis.ConnectionPool.from_url(self.redis_url, decode_responses=False)
                self.client = redis.Redis(connection_pool=pool)
            else:
                raise RedisConnectionError("No valid Redis configuration provided.")
                
            # Register the Lua script
            self._script_obj = self.client.register_script(SLIDING_WINDOW_SCRIPT)
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            if not self.fail_open:
                raise RedisConnectionError(f"Failed to connect to Redis: {e}")
            
    def is_connected(self) -> bool:
        """Check if Redis is connected and pingable."""
        if not self.client:
            return False
        try:
            return bool(self.client.ping())
        except redis.RedisError:
            return False

    def execute_sliding_window(self, key: str, limit: int, window_ms: int, now_ms: int, request_id: str) -> Optional[Tuple[int, int, int]]:
        """
        Execute the sliding window Lua script.
        Returns: (allowed, remaining, retry_after)
        If fail_open is true and Redis fails, returns None.
        """
        if not self.client or not self._script_obj:
            if self.fail_open:
                return None
            raise RedisConnectionError("Redis client or Lua script not initialized")
            
        try:
            # Returns a list of [allowed(1/0), remaining, retry_after]
            res = self._script_obj(keys=[key], args=[limit, window_ms, now_ms, request_id])
            return (int(res[0]), int(res[1]), int(res[2]))
        except redis.RedisError as e:
            logger.error(f"Redis rate limiting execution failed: {e}")
            if self.fail_open:
                return None
            raise RedisConnectionError(f"Redis operation failed: {e}")

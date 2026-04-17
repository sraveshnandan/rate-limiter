# API Reference

## `RateLimiter`

**Constructor**
```python
RateLimiter(
    redis_url: Optional[str] = None,
    redis_nodes: Optional[List[Dict[str, Any]]] = None,
    limit: Optional[int] = None,
    window: Optional[int] = None,
    limits: Optional[List[dict]] = None,
    key_prefix: str = "rate_limit",
    key_generator: Optional[Callable] = None,
    skip: Optional[Callable] = None,
    message: str = "Too Many Requests",
    error_message: str = "Rate limit exceeded",
    status_code: int = 429,
    fail_open: bool = True
)
```

### Parameters
- **`redis_url`** (`str`, optional): Standard Redis URI (`redis://localhost:6379/0`).
- **`redis_nodes`** (`List[dict]`, optional): Used to connect to a Redis Cluster. Each dict should have `host` and `port`.
- **`limit`** (`int`, optional): Max requests allowed in the window. Must be present if `limits` is not.
- **`window`** (`int`, optional): Re-evaluation window size in seconds. Must be present if `limits` is not.
- **`limits`** (`List[dict]`, optional): Setting up tiered limits list `[{"limit": X, "window": Y, "scope": Z}]`.
- **`key_prefix`** (`str`, optional): Redis Key prefix namespace. Default `rate_limit`.
- **`key_generator`** (`callable`, optional): Extract a specific string identifier from `request`. Ex: `lambda req: req.client.host`.
- **`skip`** (`callable`, optional): Skip rate-limiting when returns True. Ex: `lambda req: req.path == "/health"`.
- **`message`** (`str`): Response HTTP error property string.
- **`error_message`** (`str`): General textual UI response phrase.
- **`status_code`** (`int`): Defines the HTTP response string, typically 429.
- **`fail_open`** (`bool`): Will automatically skip Rate Limiting if the Redis server goes down rather than block all requests. Default `True`.

### Methods
- **`check_rate_limit(identifier: str, endpoint: str) -> RateLimitResult`**: Validates limit using Redis atomic scripts.

## `RateLimitResult`
Dataclass capturing the request state:
- `allowed (bool)`: Returns True if within window.
- `remaining (int)`: Number of requests left in the active window.
- `retry_after (int)`: Total seconds remaining before rate limiting is lifted completely.
- `limit (int)`: Echo total max configuration.
- `window (int)`: Echo window configuration.
- `to_http_headers() -> dict`: Emits Standard RateLimit header keys.

# rate_limiter

A production-grade rate limiting library for Python .

The library acts as middleware between API requests and backend services, using Redis as a distributed memory store. It supports sliding window algorithms to control traffic precisely and provides out-of-the-box support for FastAPI, Flask, and Django.

## Installation

```bash
pip install -r requirements.txt
# Or if distributed as a package:
# pip install rate-limiter
```

## Quickly Setup Your Framework

### FastAPI Middleware
```python
from fastapi import FastAPI
from rate_limiter import RateLimiter, FastAPIMiddleware

app = FastAPI()

limiter = RateLimiter(
    redis_url="redis://localhost:6379",
    limit=100,
    window=60,
)

app.add_middleware(FastAPIMiddleware, limiter=limiter)

@app.get("/api/data")
async def get_data():
    return {"data": "success"}
```

### Flask Decorator
```python
from flask import Flask
from rate_limiter import rate_limit

app = Flask(__name__)

@app.route("/api/data")
@rate_limit(redis_url="redis://localhost:6379", limit=100, window=60)
def get_data():
    return {"data": "success"}
```

### Django Middleware
```python
# In settings.py
MIDDLEWARE = [
    'rate_limiter.adapters.django_adapter.DjangoRateLimiter',
    # ...
]

RATE_LIMITER_CONFIG = {
    'redis_url': 'redis://localhost:6379',
    'limit': 100,
    'window': 60,
}
```

## Advanced Examples

### Multiple Limits (Tiered)
```python
from rate_limiter import RateLimiter

limiter = RateLimiter(
    redis_url="redis://localhost:6379",
    limits=[
        {"scope": "global", "limit": 10000, "window": 60},
        {"scope": "user", "limit": 1000, "window": 60},
        {"scope": "endpoint", "limit": 100, "window": 60},
    ]
)
```

### Custom Key Generator
```python
def custom_key(request):
    return request.headers.get("X-API-Key", "anonymous")

limiter = RateLimiter(
    redis_url="redis://localhost:6379",
    limit=5000,
    window=3600,
    key_generator=custom_key,
)
```

### Skip Endpoints
```python
limiter = RateLimiter(
    redis_url="redis://localhost:6379",
    limit=100,
    window=60,
    skip=lambda req: req.url.path.startswith("/health"),
)
```

### Redis Cluster
```python
limiter = RateLimiter(
    redis_nodes=[
        {"host": "redis1.example.com", "port": 6379},
        {"host": "redis2.example.com", "port": 6379},
        {"host": "redis3.example.com", "port": 6379},
    ],
    limit=100,
    window=60,
)
```

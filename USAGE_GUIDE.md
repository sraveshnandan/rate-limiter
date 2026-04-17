# Rate Limiter Usage Guide

A simple, step-by-step guide to integrating the `rate-limiter` library into your Python services.

## 1. Installation

First, install the library and its dependencies:

```bash
pip install -r requirements.txt
```

## 2. Basic Configuration

To use the rate limiter, you need a Redis instance. You can configure the `RateLimiter` with a Redis URL.

```python
from rate_limiter import RateLimiter

limiter = RateLimiter(
    redis_url="redis://localhost:6379",
    limit=100,  # Number of requests
    window=60,   # Time window in seconds
)
```

## 3. Integration with Frameworks

### FastAPI

Use the middleware to protect all routes or specific ones.

```python
from fastapi import FastAPI
from rate_limiter.adapters.fastapi_adapter import RateLimiterMiddleware

app = FastAPI()
# Add middleware to the app
app.add_middleware(RateLimiterMiddleware, limiter=limiter)

@app.get("/")
async def root():
    return {"message": "Hello World"}
```

### Flask

Use the `@rate_limit` decorator on your routes.

```python
from flask import Flask
from rate_limiter.adapters.flask_adapter import rate_limit

app = Flask(__name__)

@app.route("/")
@rate_limit(limiter=limiter)
def hello():
    return "Hello World"
```

### Django

Add the middleware to your `MIDDLEWARE` list in `settings.py`.

```python
# settings.py
MIDDLEWARE = [
    'rate_limiter.adapters.django_adapter.DjangoRateLimiter',
    # ... other middlewares
]

RATE_LIMITER_CONFIG = {
    'redis_url': 'redis://localhost:6379',
    'limit': 100,
    'window': 60,
}
```

## 4. Advanced: Custom Identification

By default, the rate limiter uses the client's IP address. To limit by User ID or API Key, provide a `key_generator` function.

```python
def get_user_id(request):
    # For FastAPI/Starlette request objects
    return request.headers.get("X-User-ID", "anonymous")

limiter = RateLimiter(
    redis_url="redis://localhost:6379",
    limit=5,
    window=60,
    key_generator=get_user_id
)
```

## 5. Summary of Headers

The library automatically adds rate limit info to your response headers:
- `X-RateLimit-Limit`: Maximum requests allowed.
- `X-RateLimit-Remaining`: Remaining requests in current window.
- `X-RateLimit-Reset`: Seconds until the limit resets.

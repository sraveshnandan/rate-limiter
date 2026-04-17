import sys
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add parent directory to sys.path to easily import rate_limiter natively
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rate_limiter.core import RateLimiter
from rate_limiter.config import LimitTier
from rate_limiter.adapters.fastapi_adapter import RateLimiterMiddleware

app = FastAPI(title="Rate Limiter Test Backend")


def custom_key_generator(request: Request):
    """Rate limit by x-user-id header if present, otherwise IP."""
    user_id = request.headers.get("x-user-id")
    if user_id:
        return user_id
    return request.client.host if request.client else "unknown"


def skip_rules(request: Request):
    """Skip rate limiting for health endpoint AND CORS preflight OPTIONS requests."""
    if request.method == "OPTIONS":
        return True
    return request.url.path == "/api/health"


# Initialize rate limiter
limiter = RateLimiter(
    redis_url="rediss://default:gQAAAAAAAWJMAAIncDFkMjQ5Mzk0NGI5ZmI0M2YyYTc4ZDJmYzQ4YWYyODNkY3AxOTA3MDA@trusted-flea-90700.upstash.io:6379",
    limits=[
        LimitTier(scope="global", limit=10, window=60),  # 10 requests / 60s
        LimitTier(scope="endpoint", limit=4, window=20),  # 4 requests / 20s
    ],
    key_generator=custom_key_generator,
    skip=skip_rules,
)

# Add middleware
app.add_middleware(RateLimiterMiddleware, limiter=limiter)

# Ensure CORSMiddleware is added AFTER RateLimiterMiddleware so it wraps it
# (FastAPI middleware runs in reverse order of addition, so this makes CORS the outermost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.get("/api/basic")
async def basic_endpoint():
    return {"message": "Success from basic endpoint"}


@app.get("/api/custom")
async def custom_endpoint(request: Request):
    user_id = request.headers.get("x-user-id", "None")
    return {"message": f"Success from custom endpoint", "user_id": user_id}


@app.get("/api/health")
async def health_endpoint():
    return {"message": "Health endpoint - skipped by rate limiter"}


class ConfigUpdate(BaseModel):
    global_limit: int
    global_window: int
    endpoint_limit: int
    endpoint_window: int


@app.post("/api/config")
async def update_config(config: ConfigUpdate):
    limiter.config.limits = [
        LimitTier(
            scope="global", limit=config.global_limit, window=config.global_window
        ),
        LimitTier(
            scope="endpoint", limit=config.endpoint_limit, window=config.endpoint_window
        ),
    ]
    return {"message": "Rate limits hot-swapped successfully!", "config": config.dict()}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

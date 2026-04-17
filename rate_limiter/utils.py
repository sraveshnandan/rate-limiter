"""Helper functions for the rate limiter."""
from typing import Any

def get_client_ip(request: Any) -> str:
    """Attempt to extract client IP from various framework request objects."""
    if hasattr(request, "client") and request.client:
        return request.client.host # FastAPI/Starlette
    if hasattr(request, "remote_addr"):
        return request.remote_addr # Flask
    if hasattr(request, "META"):
        return request.META.get("REMOTE_ADDR", "unknown") # Django
    return "unknown"

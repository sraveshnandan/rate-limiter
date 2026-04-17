"""FastAPI/Starlette middleware adapter."""
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.concurrency import run_in_threadpool
from rate_limiter.core import RateLimiter

class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limiter: RateLimiter):
        super().__init__(app)
        self.limiter = limiter

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Check skip condition
        if self.limiter.config.skip and self.limiter.config.skip(request):
            return await call_next(request)

        # Determine identifier
        if self.limiter.config.key_generator:
            identifier = self.limiter.config.key_generator(request)
        else:
            # Default to client IP
            identifier = request.client.host if request.client else "unknown"

        endpoint = request.url.path

        # Execute rate limiting in a threadpool to not block the async event loop
        result = await run_in_threadpool(self.limiter.check_rate_limit, identifier, endpoint)

        if not result.allowed:
            headers = result.to_http_headers()
            content = {
                "error": self.limiter.config.message,
                "message": self.limiter.config.error_message,
                "retry_after": result.retry_after,
                "limit": result.limit,
                "window": result.window
            }
            return JSONResponse(
                content=content,
                status_code=self.limiter.config.status_code,
                headers=headers
            )

        # Allow request and append headers
        response = await call_next(request)
        for key, value in result.to_http_headers().items():
            response.headers[key] = value
            
        return response

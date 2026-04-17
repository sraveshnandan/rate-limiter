"""Flask middleware/decorator adapter."""
# While we implement generic route decorators in decorators.py,
# this file can serve specific Flask usages.
from functools import wraps
from rate_limiter.core import RateLimiter

def rate_limit(limiter: RateLimiter = None, **kwargs):
    """
    Decorator for Flask routes.
    If limiter is not provided, creates one from kwargs.
    """
    if not limiter:
        limiter = RateLimiter(**kwargs)
        
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **route_kwargs):
            try:
                from flask import request, make_response, jsonify
            except ImportError:
                raise ImportError("Flask is required to use the flask rate_limit decorator")

            if limiter.config.skip and limiter.config.skip(request):
                return f(*args, **route_kwargs)
                
            if limiter.config.key_generator:
                identifier = limiter.config.key_generator(request)
            else:
                identifier = request.remote_addr or "unknown"
                
            endpoint = request.path
            result = limiter.check_rate_limit(identifier, endpoint)
            
            if not result.allowed:
                content = {
                    "error": limiter.config.message,
                    "message": limiter.config.error_message,
                    "retry_after": result.retry_after,
                    "limit": result.limit,
                    "window": result.window
                }
                response = make_response(jsonify(content), limiter.config.status_code)
                for key, value in result.to_http_headers().items():
                    response.headers[key] = value
                return response
                
            response = make_response(f(*args, **route_kwargs))
            for key, value in result.to_http_headers().items():
                response.headers[key] = value
            return response
            
        return wrapped
    return decorator

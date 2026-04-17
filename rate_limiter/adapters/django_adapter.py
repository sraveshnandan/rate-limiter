"""Django middleware adapter."""
from django.conf import settings
from django.http import JsonResponse
from rate_limiter.core import RateLimiter

class DjangoRateLimiter:
    """Middleware for Django."""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Load config from Django settings
        config = getattr(settings, 'RATE_LIMITER_CONFIG', {})
        self.limiter = RateLimiter(**config)

    def __call__(self, request):
        if self.limiter.config.skip and self.limiter.config.skip(request):
            return self.get_response(request)
            
        if self.limiter.config.key_generator:
            identifier = self.limiter.config.key_generator(request)
        else:
            # Django default IP
            identifier = request.META.get('REMOTE_ADDR', 'unknown')
            
        endpoint = request.path
        result = self.limiter.check_rate_limit(identifier, endpoint)
        
        if not result.allowed:
            content = {
                "error": self.limiter.config.message,
                "message": self.limiter.config.error_message,
                "retry_after": result.retry_after,
                "limit": result.limit,
                "window": result.window
            }
            response = JsonResponse(content, status=self.limiter.config.status_code)
            for key, value in result.to_http_headers().items():
                response[key] = value
            return response
            
        response = self.get_response(request)
        for key, value in result.to_http_headers().items():
            response[key] = value
        return response

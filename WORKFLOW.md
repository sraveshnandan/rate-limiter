# Rate Limiter Platform Workflow

This document explains the end-to-end request lifecycle and how the rate limiter processes each request conceptually and technically.

## 1. Request Interception
- When a client sends an HTTP request to the application, it first hits the web framework's middleware stack.
- The `RateLimiterMiddleware` (e.g., FastAPI, Flask, Django adapter) intercepts the request before it reaches the core application logic.

## 2. Evaluation Phase
- **Bypass Check (`skip` condition):** The middleware evaluates user-defined rules. If the request matches a skip condition (e.g., health check endpoints or preflight OPTIONS requests), it bypasses the rate limiter and proceeds immediately to the application.
- **Identifier Generation:** If the request isn't skipped, the `key_generator` extracts identifying information from the request. This can be an IP address, a user session token, or an API key (e.g., `x-user-id`).

## 3. Rate Limit Execution
- For each tier defined in the configuration (e.g., 100 requests/minute globally AND 10 requests/second per endpoint):
  1. A unique string identifier is constructed: `[prefix]:[scope]:[identifier]:[endpoint]`.
  2. The application executes a unified Lua script within Redis via `RedisClientWrapper`.
  3. The **Sliding Window Algorithm** is executed atomically inside Redis:
     - Old requests outside the current time window are cleared.
     - The current request is added to the sorted set with its timestamp.
     - The total count within the window is compared against the limit threshold.

## 4. Decision & Response
- **If Allowed:** 
  - The middleware passes processing back to the API endpoint.
  - Upon returning, standard response headers like `ratelimit-limit` and `ratelimit-remaining` are attached, granting visibility to the client.
- **If Throttled:** 
  - The middleware immediately halts processing and aborts the request.
  - Returns an HTTP **429 Too Many Requests** error along with an explicit `retry-after` header so clients know when they can resume.
- **Fail-Open Mechanism:**
  - If the Redis connection goes entirely offline, an optional `fail_open` configuration allows requests to bypass rate-limiting rather than crashing the primary application services, preserving uptime.

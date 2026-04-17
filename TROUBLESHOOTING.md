# Troubleshooting Guide

## Common Issues and Solutions

### 1. ModuleNotFound: "No module named 'redis'"
**Effect**: Script fails instantly upon initialization.
**Fix**: Ensure `redis` is pip installed. If using clustering, install `redis[cluster]`.

### 2. Rate Limit Headers Absent from Response
**Effect**: 429 Error blocks traffic, but rate limit metric headers do not appear.
**Fix**: Using framework-specific manual decorators without explicitly adding `.to_http_headers()` attributes on your specific Response Builder object. We highly recommend standard Middleware configuration for automatic Header mounting.

### 3. Redis is down and ALL requests are returning 500 External Errors
**Effect**: API availability hinges immediately on Redis uptime.
**Fix**: Make sure `fail_open=True` (This is the Default) in your config. This allows HTTP pass-through logic seamlessly if socket connections drop.

### 4. Sliding Window isn't exactly mapping 1:1 on simultaneous bursts
**Effect**: Rate Limiter is tracking requests seemingly "out of order" during tight loops.
**Fix**: Ensure you have implemented the `SLIDING_WINDOW_SCRIPT` Lua methodology correctly. The lua atomic pipeline relies on Server Timestamp precision (`ARGV[3]`). Minor microsecond delays due to Python OS-level thread-locking in milliseconds can drift scoring. If you require hyper-precise time tracking, consider pushing timestamp logic inside the Lua Evaluation inside Redis directly via `TIME`.

## Performance Tuning
- **Install `hiredis`**: The C-binding wrapper parses standard payload requests faster over socket connections.
- **Connection Pools**: We enable connection pooling out-of-the-box inside `RedisClientWrapper`. Do not instantiate multiple `RateLimiter()` objects per Request (this causes socket drain exhaustion). Keep `limiter = RateLimiter(...)` global and pass it inside Middleware.

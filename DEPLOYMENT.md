# Deployment Guide

`rate_limiter` uses distributed storage (Redis) meaning it naturally scales across containers or worker processes.

## Docker Setup

### Simple Single-Instance Redis (Docker Compose)
A standard implementation utilizing Docker Compose could setup the Redis store parallel to your API instance.
```yaml
version: '3.8'
services:
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
```

### Redis Scaling Strategies
At scale (`>50k req/s`), single-threaded Redis might bottleneck CPU resources. In horizontal scenarios, you ought to setup a **Redis Cluster**. `rate_limiter` has built in support.

```python
limiter = RateLimiter(
    redis_nodes=[
        {"host": "redis-node-1.cluster.local", "port": 6379},
        {"host": "redis-node-2.cluster.local", "port": 6379},
        {"host": "redis-node-3.cluster.local", "port": 6379},
    ],
    limit=1000,
    window=60,
)
```

**Memory Expectations:**
Memory usage primarily holds the rate limit sliding-window metrics. Ensure your Redis persistence strategy avoids persisting this data rigidly since caching resets auto-expire via Redis TTL mechanism (which keeps footprint minimal to `<1KB per active 1000/s window`).
*To scale perfectly*, `hiredis` is strongly recommended for faster response parsing on heavy loads.

## Kubernetes Deployment
Configure the library using `fail_open=True` natively (since doing so won't permanently crash the API Pods upon network separation from the cluster). 
In Kubernetes, make sure Redis connection failures don't drop HTTP requests during node reallocation. 
```yaml
# A Standard StatefulSet is ideal for configuring Redis Cluster on K8s
# Connect directly to your internal headless Service via `redis_nodes`
```

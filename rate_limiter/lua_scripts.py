"""Lua scripts for atomic Redis operations."""

# Sliding window Lua script
# KEYS[1]: rate limit key (e.g., rate_limit:ip:endpoint)
# ARGV[1]: limit (max requests)
# ARGV[2]: window in milliseconds
# ARGV[3]: current timestamp in milliseconds
# ARGV[4]: unique request ID for atomic concurrency
SLIDING_WINDOW_SCRIPT = """
local key = KEYS[1]
local limit = tonumber(ARGV[1])
local window_ms = tonumber(ARGV[2])
local now_ms = tonumber(ARGV[3])
local req_id = ARGV[4]
local window_start = now_ms - window_ms

-- Remove expired entries older than window_start
redis.call('ZREMRANGEBYSCORE', key, '-inf', window_start)

-- Count remaining requests in the window
local count = redis.call('ZCARD', key)

if count < limit then
    -- Allow the request, ensuring uniqueness with req_id
    redis.call('ZADD', key, now_ms, now_ms .. "-" .. req_id)
    -- Extend TTL to auto-cleanup (window_ms + 60s buffer for safety)
    redis.call('EXPIRE', key, math.ceil(window_ms / 1000) + 60)
    return {1, limit - count - 1, 0}
else
    -- Reject the request
    local oldest = redis.call('ZRANGE', key, 0, 0, 'WITHSCORES')
    local retry_after = 0
    if oldest and oldest[1] then
        retry_after = math.ceil((oldest[2] + window_ms - now_ms) / 1000)
    else
        retry_after = math.ceil(window_ms / 1000)
    end
    -- Keep TTL accurate, even if request rejected
    redis.call('EXPIRE', key, math.ceil(window_ms / 1000) + 60)
    return {0, 0, math.max(1, retry_after)}
end
"""

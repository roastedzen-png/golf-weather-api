"""
Redis Client Configuration

Async Redis connection for rate limiting and caching.
"""

import redis.asyncio as redis
from app.config import settings

# Redis client instance (created lazily)
_redis_client = None


def get_redis_client():
    """Get the Redis client instance.

    Returns None if Redis is not configured (graceful degradation).
    """
    global _redis_client

    if _redis_client is not None:
        return _redis_client

    if not settings.REDIS_URL:
        return None

    _redis_client = redis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
    )

    return _redis_client


async def init_redis():
    """Initialize and verify Redis connection."""
    client = get_redis_client()
    if client is not None:
        await client.ping()
    return client


async def close_redis():
    """Close Redis connection."""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None

"""
Rate Limiting Middleware

Uses Redis for distributed rate limiting with sliding window.
"""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time

from app.config import settings

# Paths excluded from rate limiting
EXCLUDED_PATHS = ["/", "/docs", "/redoc", "/openapi.json"]

# Rate limits per client tier (requests per minute)
RATE_LIMITS = {
    "free": 60,
    "standard": 1000,
    "professional": 5000,
    "enterprise": 20000,
    "inrange_prod": 20000,
    "inrange_test": 1000,
    "admin": 10000,
    "default": 1000,
}


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce rate limits using Redis."""

    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip rate limiting for excluded paths
        if any(request.url.path.startswith(path) for path in EXCLUDED_PATHS):
            return await call_next(request)

        # Import here to avoid circular imports
        from app.redis_client import get_redis_client

        redis_client = get_redis_client()

        # If Redis is not available, skip rate limiting (graceful degradation)
        if redis_client is None:
            return await call_next(request)

        # Get client ID (set by auth middleware)
        client_id = getattr(request.state, "client_id", "anonymous")

        # Get rate limit for this client
        rate_limit = RATE_LIMITS.get(client_id, RATE_LIMITS["default"])

        # Redis key for this client's rate limit window
        current_minute = int(time.time() // 60)
        redis_key = f"ratelimit:{client_id}:{current_minute}"

        try:
            # Increment counter
            current_count = await redis_client.incr(redis_key)

            # Set expiry on first request in window
            if current_count == 1:
                await redis_client.expire(redis_key, 60)

            # Check if over limit
            if current_count > rate_limit:
                # Get TTL for reset time
                ttl = await redis_client.ttl(redis_key)
                if ttl < 0:
                    ttl = 60

                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": {
                            "code": "RATE_LIMIT_EXCEEDED",
                            "message": f"Rate limit exceeded. Limit: {rate_limit}/minute.",
                            "retry_after": ttl,
                        }
                    },
                    headers={
                        "X-RateLimit-Limit": str(rate_limit),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(int(time.time()) + ttl),
                        "Retry-After": str(ttl),
                    },
                )

            # Process request
            response = await call_next(request)

            # Add rate limit headers
            response.headers["X-RateLimit-Limit"] = str(rate_limit)
            response.headers["X-RateLimit-Remaining"] = str(
                max(0, rate_limit - current_count)
            )
            response.headers["X-RateLimit-Reset"] = str(current_minute * 60 + 60)

            return response

        except HTTPException:
            raise
        except Exception:
            # If Redis fails, allow request through (graceful degradation)
            return await call_next(request)

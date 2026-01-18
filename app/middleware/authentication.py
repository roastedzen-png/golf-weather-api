"""
API Key Authentication Middleware

Validates X-API-Key header against stored hashes.
Checks both environment variables and database.
"""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import hashlib
import asyncpg
from app.config import settings

# Paths that don't require X-API-Key authentication
# (admin routes have their own authentication)
PUBLIC_PATHS = [
    "/",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/api/v1/health",
    "/api/v1/admin",
    "/admin-api",    # Admin dashboard API (uses Google OAuth)
    "/admin",        # Admin dashboard static files
    "/v1/health",    # Legacy health endpoint
    "/docs/client",  # Client documentation
    "/api/request-key",  # API key request form (public)
    "/api/contact",      # Contact form (public)
]

# Database connection pool for API key lookups
_auth_db_pool = None


async def get_auth_db_pool():
    """Get or create database connection pool for auth."""
    global _auth_db_pool
    if _auth_db_pool is None:
        db_url = settings.DATABASE_URL
        if db_url:
            if db_url.startswith("postgresql+asyncpg://"):
                db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
            try:
                _auth_db_pool = await asyncpg.create_pool(db_url, min_size=1, max_size=5)
            except Exception:
                pass
    return _auth_db_pool


async def check_database_key(key_hash: str) -> tuple:
    """Check if API key exists in database and is active. Returns (client_name, api_key_id) or (None, None)."""
    pool = await get_auth_db_pool()
    if not pool:
        return None, None

    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT id, client_name FROM admin_api_keys
                WHERE key_hash = $1 AND status = 'active'
                """,
                key_hash
            )
            if row:
                # Update last_used and request counters
                await conn.execute(
                    """
                    UPDATE admin_api_keys
                    SET last_used_at = NOW(),
                        requests_today = requests_today + 1,
                        total_requests = total_requests + 1
                    WHERE id = $1
                    """,
                    row["id"]
                )
                return row["client_name"], row["id"]
    except Exception:
        pass

    return None, None


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware to authenticate API requests using X-API-Key header."""

    async def dispatch(self, request: Request, call_next):
        # Skip auth for public paths
        path = request.url.path
        if any(path == p or path.startswith(p + "/") for p in PUBLIC_PATHS):
            return await call_next(request)

        # Get API key from header
        api_key = request.headers.get("X-API-Key")

        if not api_key:
            raise HTTPException(
                status_code=401,
                detail={
                    "error": {
                        "code": "MISSING_API_KEY",
                        "message": "API key is required. Include X-API-Key header.",
                    }
                },
            )

        # Hash the provided key
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        # Check against environment variable keys first
        client_id = None
        api_key_id = None
        for client, stored_hash in settings.API_KEYS.items():
            if key_hash == stored_hash:
                client_id = client
                break

        # If not found in env vars, check database
        if not client_id:
            client_id, api_key_id = await check_database_key(key_hash)

        if not client_id:
            raise HTTPException(
                status_code=401,
                detail={
                    "error": {
                        "code": "INVALID_API_KEY",
                        "message": "The API key provided is invalid or expired.",
                    }
                },
            )

        # Store client ID and API key ID in request state for logging and rate limiting
        request.state.client_id = client_id
        request.state.api_key_id = api_key_id

        return await call_next(request)

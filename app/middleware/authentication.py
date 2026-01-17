"""
API Key Authentication Middleware

Validates X-API-Key header against stored hashes.
"""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import hashlib
from app.config import settings

# Paths that don't require authentication
PUBLIC_PATHS = [
    "/",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/api/v1/health",
]


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

        # Check against valid keys
        client_id = None
        for client, stored_hash in settings.API_KEYS.items():
            if key_hash == stored_hash:
                client_id = client
                break

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

        # Store client ID in request state for logging and rate limiting
        request.state.client_id = client_id

        return await call_next(request)

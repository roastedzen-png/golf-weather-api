"""
Admin Router

Endpoints for usage statistics and administration.
Requires admin API key.
"""

from fastapi import APIRouter, Depends, HTTPException, Header
from datetime import date, timedelta
import hashlib

from app.config import settings
from app.services.usage import UsageService
from app.database import get_db

router = APIRouter()


async def verify_admin_key(x_admin_key: str = Header(None), x_api_key: str = Header(None)):
    """Verify admin API key from either header."""
    # Try X-Admin-Key first, then fall back to X-API-Key
    admin_key = x_admin_key or x_api_key

    if not admin_key:
        raise HTTPException(
            status_code=403,
            detail={
                "error": {
                    "code": "ADMIN_KEY_REQUIRED",
                    "message": "Admin API key is required. Include X-Admin-Key header.",
                }
            },
        )

    key_hash = hashlib.sha256(admin_key.encode()).hexdigest()

    # Check against admin key hash
    if key_hash != settings.ADMIN_KEY_HASH:
        # Also check if it's the admin client in API_KEYS
        if settings.API_KEYS.get("admin") != key_hash:
            raise HTTPException(
                status_code=403,
                detail={
                    "error": {
                        "code": "INVALID_ADMIN_KEY",
                        "message": "The admin API key provided is invalid.",
                    }
                },
            )

    return True


@router.get("/usage/{client_id}")
async def get_client_usage(
    client_id: str,
    days: int = 30,
    db=Depends(get_db),
    admin=Depends(verify_admin_key),
):
    """
    Get usage statistics for a specific client.

    Requires admin API key.

    Args:
        client_id: The client ID to get usage for
        days: Number of days to look back (default 30)
    """
    if db is None:
        raise HTTPException(
            status_code=503,
            detail={
                "error": {
                    "code": "DATABASE_NOT_CONFIGURED",
                    "message": "Database is not configured. Usage tracking unavailable.",
                }
            },
        )

    service = UsageService(db)

    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    usage = await service.get_client_usage(client_id, start_date, end_date)
    summary = await service.get_usage_summary(client_id)

    return {
        "client_id": client_id,
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
        },
        "summary": {
            "total_requests": summary["total_requests"],
            "total_errors": summary["total_errors"],
            "avg_latency_ms": summary["avg_latency"],
            "first_request": summary["first_request"].isoformat() if summary["first_request"] else None,
            "last_request": summary["last_request"].isoformat() if summary["last_request"] else None,
        },
        "daily": [
            {
                "date": u.date.isoformat(),
                "endpoint": u.endpoint,
                "requests": u.request_count,
                "errors": u.error_count,
                "avg_latency_ms": round(u.total_latency_ms / u.request_count, 2) if u.request_count else 0,
            }
            for u in usage
        ],
    }


@router.get("/usage")
async def get_all_usage(
    days: int = 7,
    db=Depends(get_db),
    admin=Depends(verify_admin_key),
):
    """
    Get usage statistics for all clients.

    Requires admin API key.

    Args:
        days: Number of days to look back (default 7)
    """
    if db is None:
        raise HTTPException(
            status_code=503,
            detail={
                "error": {
                    "code": "DATABASE_NOT_CONFIGURED",
                    "message": "Database is not configured. Usage tracking unavailable.",
                }
            },
        )

    service = UsageService(db)
    clients_usage = await service.get_all_clients_usage(days)

    return {
        "period": {
            "start": (date.today() - timedelta(days=days)).isoformat(),
            "end": date.today().isoformat(),
        },
        "clients": clients_usage,
    }


@router.get("/keys")
async def list_api_keys(admin=Depends(verify_admin_key)):
    """
    List all configured API key client IDs (not the actual keys).

    Requires admin API key.
    """
    return {
        "clients": list(settings.API_KEYS.keys()),
        "count": len(settings.API_KEYS),
    }

"""
Health Check Router

Endpoints for monitoring and readiness checks.
"""

from fastapi import APIRouter, Depends
from datetime import datetime
from sqlalchemy import text

from app.config import settings
from app.redis_client import get_redis_client
from app.database import get_db

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring services.

    Returns the API status, version, and current timestamp.
    No authentication required.
    """
    checks = {
        "api": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    # Check Redis if configured
    redis_client = get_redis_client()
    if redis_client is not None:
        try:
            await redis_client.ping()
            checks["redis"] = "healthy"
        except Exception as e:
            checks["redis"] = "unhealthy"
            checks["redis_error"] = str(e)
    else:
        checks["redis"] = "not_configured"

    # Overall status
    all_healthy = checks["api"] == "healthy"
    if "redis" in checks and checks["redis"] == "unhealthy":
        all_healthy = False

    return {
        "status": "healthy" if all_healthy else "degraded",
        "checks": checks,
    }


@router.get("/health/ready")
async def readiness_check(db=Depends(get_db)):
    """
    Readiness check - verifies all dependencies are ready.

    Used by Railway/Kubernetes to know when to route traffic.
    """
    checks = {}

    # Check database if configured
    if db is not None:
        try:
            await db.execute(text("SELECT 1"))
            checks["database"] = "ready"
        except Exception as e:
            checks["database"] = "not_ready"
            checks["database_error"] = str(e)
    else:
        checks["database"] = "not_configured"

    # Check Redis if configured
    redis_client = get_redis_client()
    if redis_client is not None:
        try:
            await redis_client.ping()
            checks["redis"] = "ready"
        except Exception as e:
            checks["redis"] = "not_ready"
            checks["redis_error"] = str(e)
    else:
        checks["redis"] = "not_configured"

    # Overall readiness
    all_ready = all(
        v in ("ready", "not_configured")
        for k, v in checks.items()
        if not k.endswith("_error")
    )

    return {
        "status": "ready" if all_ready else "not_ready",
        "checks": checks,
    }


@router.get("/health/live")
async def liveness_check():
    """
    Liveness check - verifies the API process is running.

    Used by Railway/Kubernetes to detect hung processes.
    """
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat() + "Z"}

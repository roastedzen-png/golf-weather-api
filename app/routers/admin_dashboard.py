"""
Admin Dashboard Router

Google OAuth-protected endpoints for the admin dashboard UI.
Separate from the X-Admin-Key protected API endpoints.
"""

import os
import secrets
import hashlib
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Header, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import asyncpg
import io
import csv

from app.config import settings

# ============================================
# CONFIGURATION
# ============================================

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "golfphysicsio@gmail.com")

# Rate limits per tier (requests per minute)
RATE_LIMITS = {
    "free": 60,
    "standard": 1000,
    "enterprise": 20000
}

# ============================================
# DATABASE CONNECTION
# ============================================

_admin_db_pool = None

async def get_admin_db_pool():
    """Get or create database connection pool for admin dashboard."""
    global _admin_db_pool
    if _admin_db_pool is None:
        db_url = settings.DATABASE_URL
        if db_url.startswith("postgresql+asyncpg://"):
            db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
        if db_url:
            _admin_db_pool = await asyncpg.create_pool(db_url, min_size=1, max_size=5)
    return _admin_db_pool

# ============================================
# AUTHENTICATION
# ============================================

async def verify_google_token(authorization: str = Header(None)) -> str:
    """Verify Google OAuth token and check admin email."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail={"error": {"code": "MISSING_TOKEN", "message": "Authorization header required"}}
        )

    token = authorization.replace("Bearer ", "")

    # Import here to avoid startup issues if google-auth not installed
    try:
        from google.oauth2 import id_token
        from google.auth.transport import requests as google_requests
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail={"error": {"code": "AUTH_NOT_CONFIGURED", "message": "Google Auth not installed"}}
        )

    if not GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=500,
            detail={"error": {"code": "AUTH_NOT_CONFIGURED", "message": "GOOGLE_CLIENT_ID not set"}}
        )

    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            GOOGLE_CLIENT_ID
        )

        email = idinfo.get("email", "")

        if email.lower() != ADMIN_EMAIL.lower():
            raise HTTPException(
                status_code=403,
                detail={"error": {"code": "ACCESS_DENIED", "message": f"Only {ADMIN_EMAIL} can access admin dashboard"}}
            )

        return email

    except ValueError as e:
        raise HTTPException(
            status_code=401,
            detail={"error": {"code": "INVALID_TOKEN", "message": str(e)}}
        )

# ============================================
# PYDANTIC MODELS
# ============================================

class CreateApiKeyRequest(BaseModel):
    client_name: str = Field(..., min_length=1, max_length=255)
    tier: str = Field(default="free", pattern="^(free|standard|enterprise)$")
    notes: Optional[str] = None

class CreateApiKeyResponse(BaseModel):
    id: int
    client_name: str
    api_key: str
    key_prefix: str
    tier: str
    rate_limit_per_minute: int
    message: str

class ApiKeyInfo(BaseModel):
    id: int
    client_name: str
    key_prefix: str
    tier: str
    status: str
    created_at: datetime
    last_used_at: Optional[datetime]
    requests_today: int
    total_requests: int
    rate_limit_per_minute: int
    notes: Optional[str]

class UpdateStatusRequest(BaseModel):
    status: str = Field(..., pattern="^(active|disabled|revoked)$")

class UpdateTierRequest(BaseModel):
    tier: str = Field(..., pattern="^(free|standard|enterprise)$")

class DailyUsage(BaseModel):
    client_name: str
    date: str
    total_requests: int
    successful_requests: int
    error_requests: int
    avg_latency_ms: float
    error_rate_percent: float

class UsageSummary(BaseModel):
    total_requests_24h: int
    total_errors_24h: int
    avg_latency_24h: float
    active_clients: int
    requests_by_tier: dict

class RequestLog(BaseModel):
    id: int
    client_name: Optional[str]
    endpoint: str
    method: str
    status_code: int
    latency_ms: float
    error_message: Optional[str]
    request_ip: Optional[str]
    created_at: datetime


class LeadInfo(BaseModel):
    id: int
    source: str
    name: str
    email: str
    company: Optional[str]
    use_case: Optional[str]
    subject: Optional[str]
    expected_volume: Optional[str]
    is_high_value: bool
    priority: str
    status: str
    created_at: datetime
    contacted_at: Optional[datetime]
    internal_notes: Optional[str]


class LeadStats(BaseModel):
    total: int
    new: int
    high_value: int
    api_requests: int
    contacts: int
    this_week: int
    this_month: int


class UpdateLeadRequest(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[str] = None
    internal_notes: Optional[str] = None

# ============================================
# ROUTER
# ============================================

router = APIRouter(prefix="/admin-api", tags=["Admin Dashboard"])

# ============================================
# MAINTENANCE
# ============================================

async def run_maintenance():
    """Run periodic maintenance tasks (cleanup old logs)."""
    pool = await get_admin_db_pool()
    if not pool:
        return 0
    try:
        async with pool.acquire() as conn:
            result = await conn.fetchval("SELECT cleanup_old_request_logs()")
            return result or 0
    except Exception:
        return 0

# ============================================
# HEALTH CHECK
# ============================================

@router.get("/health")
async def admin_dashboard_health(admin_email: str = Depends(verify_google_token)):
    """Health check for admin dashboard (requires Google OAuth)."""
    # Run maintenance in background (cleanup old logs)
    deleted = await run_maintenance()

    return {
        "status": "healthy",
        "admin": admin_email,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "maintenance": {"logs_cleaned": deleted}
    }

# ============================================
# API KEY MANAGEMENT
# ============================================

@router.post("/api-keys", response_model=CreateApiKeyResponse)
async def create_api_key(
    request: CreateApiKeyRequest,
    admin_email: str = Depends(verify_google_token)
):
    """Create a new API key for a client."""
    pool = await get_admin_db_pool()
    if not pool:
        raise HTTPException(status_code=503, detail="Database not available")

    # Generate secure API key
    random_part = secrets.token_hex(24)
    api_key = f"golf_{random_part}"
    key_prefix = f"golf_{random_part[:8]}"
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()

    async with pool.acquire() as conn:
        existing = await conn.fetchrow(
            "SELECT id FROM admin_api_keys WHERE client_name = $1 AND status != 'revoked'",
            request.client_name
        )
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"An active API key already exists for '{request.client_name}'"
            )

        row = await conn.fetchrow(
            """
            INSERT INTO admin_api_keys (client_name, key_hash, key_prefix, tier, notes)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id, client_name, key_prefix, tier
            """,
            request.client_name, key_hash, key_prefix, request.tier, request.notes
        )

    return CreateApiKeyResponse(
        id=row["id"],
        client_name=row["client_name"],
        api_key=api_key,
        key_prefix=row["key_prefix"],
        tier=row["tier"],
        rate_limit_per_minute=RATE_LIMITS[row["tier"]],
        message="Save this API key now - it will not be shown again!"
    )

@router.get("/api-keys", response_model=List[ApiKeyInfo])
async def list_api_keys(admin_email: str = Depends(verify_google_token)):
    """List all API keys."""
    pool = await get_admin_db_pool()
    if not pool:
        raise HTTPException(status_code=503, detail="Database not available")

    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT id, client_name, key_prefix, tier, status,
                   created_at, last_used_at, requests_today, total_requests, notes
            FROM admin_api_keys
            ORDER BY created_at DESC
            """
        )

    return [
        ApiKeyInfo(
            id=row["id"],
            client_name=row["client_name"],
            key_prefix=row["key_prefix"],
            tier=row["tier"],
            status=row["status"],
            created_at=row["created_at"],
            last_used_at=row["last_used_at"],
            requests_today=row["requests_today"] or 0,
            total_requests=row["total_requests"] or 0,
            rate_limit_per_minute=RATE_LIMITS.get(row["tier"], 60),
            notes=row["notes"]
        )
        for row in rows
    ]

@router.patch("/api-keys/{key_id}/status")
async def update_api_key_status(
    key_id: int,
    request: UpdateStatusRequest,
    admin_email: str = Depends(verify_google_token)
):
    """Update API key status (active/disabled/revoked)."""
    pool = await get_admin_db_pool()
    if not pool:
        raise HTTPException(status_code=503, detail="Database not available")

    async with pool.acquire() as conn:
        result = await conn.execute(
            "UPDATE admin_api_keys SET status = $1 WHERE id = $2",
            request.status, key_id
        )
        if result == "UPDATE 0":
            raise HTTPException(status_code=404, detail="API key not found")

    return {"message": f"API key status updated to {request.status}"}

@router.patch("/api-keys/{key_id}/tier")
async def update_api_key_tier(
    key_id: int,
    request: UpdateTierRequest,
    admin_email: str = Depends(verify_google_token)
):
    """Update API key tier (free/standard/enterprise)."""
    pool = await get_admin_db_pool()
    if not pool:
        raise HTTPException(status_code=503, detail="Database not available")

    async with pool.acquire() as conn:
        result = await conn.execute(
            "UPDATE admin_api_keys SET tier = $1 WHERE id = $2",
            request.tier, key_id
        )
        if result == "UPDATE 0":
            raise HTTPException(status_code=404, detail="API key not found")

    return {"message": f"API key tier updated to {request.tier}", "new_rate_limit": RATE_LIMITS[request.tier]}

@router.delete("/api-keys/{key_id}")
async def revoke_api_key(
    key_id: int,
    admin_email: str = Depends(verify_google_token)
):
    """Revoke an API key (permanent)."""
    pool = await get_admin_db_pool()
    if not pool:
        raise HTTPException(status_code=503, detail="Database not available")

    async with pool.acquire() as conn:
        result = await conn.execute(
            "UPDATE admin_api_keys SET status = 'revoked' WHERE id = $1",
            key_id
        )
        if result == "UPDATE 0":
            raise HTTPException(status_code=404, detail="API key not found")

    return {"message": "API key revoked successfully"}

# ============================================
# USAGE ANALYTICS
# ============================================

@router.get("/usage/daily", response_model=List[DailyUsage])
async def get_daily_usage(
    days: int = Query(default=30, ge=1, le=90),
    client_name: Optional[str] = None,
    admin_email: str = Depends(verify_google_token)
):
    """Get daily usage statistics."""
    pool = await get_admin_db_pool()
    if not pool:
        raise HTTPException(status_code=503, detail="Database not available")

    async with pool.acquire() as conn:
        if client_name:
            rows = await conn.fetch(
                """
                SELECT client_name, DATE(created_at) as date,
                       COUNT(*) as total_requests,
                       COUNT(*) FILTER (WHERE status_code >= 200 AND status_code < 400) as successful_requests,
                       COUNT(*) FILTER (WHERE status_code >= 400) as error_requests,
                       COALESCE(AVG(latency_ms), 0) as avg_latency_ms
                FROM admin_request_logs
                WHERE created_at > NOW() - INTERVAL '1 day' * $1 AND client_name = $2
                GROUP BY client_name, DATE(created_at)
                ORDER BY date DESC
                """, days, client_name
            )
        else:
            rows = await conn.fetch(
                """
                SELECT client_name, DATE(created_at) as date,
                       COUNT(*) as total_requests,
                       COUNT(*) FILTER (WHERE status_code >= 200 AND status_code < 400) as successful_requests,
                       COUNT(*) FILTER (WHERE status_code >= 400) as error_requests,
                       COALESCE(AVG(latency_ms), 0) as avg_latency_ms
                FROM admin_request_logs
                WHERE created_at > NOW() - INTERVAL '1 day' * $1
                GROUP BY client_name, DATE(created_at)
                ORDER BY date DESC
                """, days
            )

    return [
        DailyUsage(
            client_name=row["client_name"] or "Unknown",
            date=row["date"].isoformat(),
            total_requests=row["total_requests"],
            successful_requests=row["successful_requests"],
            error_requests=row["error_requests"],
            avg_latency_ms=round(float(row["avg_latency_ms"]), 2),
            error_rate_percent=round((row["error_requests"] / row["total_requests"] * 100) if row["total_requests"] > 0 else 0, 2)
        )
        for row in rows
    ]

@router.get("/usage/summary", response_model=UsageSummary)
async def get_usage_summary(admin_email: str = Depends(verify_google_token)):
    """Get 24-hour usage summary."""
    pool = await get_admin_db_pool()
    if not pool:
        raise HTTPException(status_code=503, detail="Database not available")

    async with pool.acquire() as conn:
        stats = await conn.fetchrow(
            """
            SELECT COUNT(*) as total_requests,
                   COUNT(*) FILTER (WHERE status_code >= 400) as total_errors,
                   COALESCE(AVG(latency_ms), 0) as avg_latency,
                   COUNT(DISTINCT client_name) as active_clients
            FROM admin_request_logs
            WHERE created_at > NOW() - INTERVAL '24 hours'
            """
        )

        tier_stats = await conn.fetch(
            """
            SELECT ak.tier, COUNT(rl.id) as request_count
            FROM admin_request_logs rl
            JOIN admin_api_keys ak ON rl.api_key_id = ak.id
            WHERE rl.created_at > NOW() - INTERVAL '24 hours'
            GROUP BY ak.tier
            """
        )

    return UsageSummary(
        total_requests_24h=stats["total_requests"] or 0,
        total_errors_24h=stats["total_errors"] or 0,
        avg_latency_24h=round(float(stats["avg_latency"] or 0), 2),
        active_clients=stats["active_clients"] or 0,
        requests_by_tier={row["tier"]: row["request_count"] for row in tier_stats}
    )

@router.get("/usage/export")
async def export_usage_csv(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    admin_email: str = Depends(verify_google_token)
):
    """Export usage data as CSV for billing."""
    pool = await get_admin_db_pool()
    if not pool:
        raise HTTPException(status_code=503, detail="Database not available")

    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT client_name, DATE(created_at) as date,
                   COUNT(*) as total_requests,
                   COUNT(*) FILTER (WHERE status_code >= 200 AND status_code < 400) as successful_requests,
                   COUNT(*) FILTER (WHERE status_code >= 400) as error_requests,
                   ROUND(AVG(latency_ms)::numeric, 2) as avg_latency_ms
            FROM admin_request_logs
            WHERE DATE(created_at) BETWEEN $1::date AND $2::date
            GROUP BY client_name, DATE(created_at)
            ORDER BY client_name, date
            """, start_date, end_date
        )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Client", "Date", "Total Requests", "Successful", "Errors", "Avg Latency (ms)"])
    for row in rows:
        writer.writerow([
            row["client_name"] or "Unknown",
            row["date"].isoformat(),
            row["total_requests"],
            row["successful_requests"],
            row["error_requests"],
            row["avg_latency_ms"]
        ])
    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=usage_{start_date}_to_{end_date}.csv"}
    )

# ============================================
# REQUEST LOGS
# ============================================

@router.get("/logs", response_model=List[RequestLog])
async def get_request_logs(
    limit: int = Query(default=100, ge=1, le=1000),
    client_name: Optional[str] = None,
    status_code: Optional[int] = None,
    endpoint: Optional[str] = None,
    admin_email: str = Depends(verify_google_token)
):
    """Get recent request logs (last 48 hours)."""
    pool = await get_admin_db_pool()
    if not pool:
        raise HTTPException(status_code=503, detail="Database not available")

    query = """
        SELECT id, client_name, endpoint, method, status_code,
               latency_ms, error_message, request_ip, created_at
        FROM admin_request_logs
        WHERE created_at > NOW() - INTERVAL '48 hours'
    """
    params = []
    param_count = 0

    if client_name:
        param_count += 1
        query += f" AND client_name = ${param_count}"
        params.append(client_name)

    if status_code:
        param_count += 1
        query += f" AND status_code = ${param_count}"
        params.append(status_code)

    if endpoint:
        param_count += 1
        query += f" AND endpoint LIKE ${param_count}"
        params.append(f"%{endpoint}%")

    param_count += 1
    query += f" ORDER BY created_at DESC LIMIT ${param_count}"
    params.append(limit)

    async with pool.acquire() as conn:
        rows = await conn.fetch(query, *params)

    return [
        RequestLog(
            id=row["id"],
            client_name=row["client_name"],
            endpoint=row["endpoint"],
            method=row["method"],
            status_code=row["status_code"],
            latency_ms=round(float(row["latency_ms"]), 2),
            error_message=row["error_message"],
            request_ip=row["request_ip"],
            created_at=row["created_at"]
        )
        for row in rows
    ]


# ============================================
# SYSTEM HEALTH & MONITORING
# ============================================

@router.get("/system/stats")
async def get_system_stats(admin_email: str = Depends(verify_google_token)):
    """Get database and system statistics."""
    pool = await get_admin_db_pool()
    if not pool:
        raise HTTPException(status_code=503, detail="Database not available")

    async with pool.acquire() as conn:
        # API Keys stats
        api_keys_stats = await conn.fetchrow("""
            SELECT
                COUNT(*) as total_keys,
                COUNT(*) FILTER (WHERE status = 'active') as active_keys,
                COUNT(*) FILTER (WHERE status = 'disabled') as disabled_keys,
                COUNT(*) FILTER (WHERE status = 'revoked') as revoked_keys,
                SUM(total_requests) as total_requests_all_time
            FROM admin_api_keys
        """)

        # Request logs stats (last 24h)
        logs_stats = await conn.fetchrow("""
            SELECT
                COUNT(*) as requests_24h,
                COUNT(*) FILTER (WHERE status_code >= 400) as errors_24h,
                ROUND(AVG(latency_ms)::numeric, 2) as avg_latency_24h
            FROM admin_request_logs
            WHERE created_at > NOW() - INTERVAL '24 hours'
        """)

        # Request logs stats (last hour)
        hourly_stats = await conn.fetchrow("""
            SELECT
                COUNT(*) as requests_1h,
                COUNT(*) FILTER (WHERE status_code >= 400) as errors_1h
            FROM admin_request_logs
            WHERE created_at > NOW() - INTERVAL '1 hour'
        """)

        # Database size
        db_size = await conn.fetchrow("""
            SELECT pg_database_size(current_database()) as size_bytes
        """)

        # Table sizes
        table_sizes = await conn.fetch("""
            SELECT
                relname as table_name,
                pg_total_relation_size(relid) as size_bytes,
                n_live_tup as row_count
            FROM pg_stat_user_tables
            ORDER BY pg_total_relation_size(relid) DESC
        """)

    # Calculate error rate
    requests_1h = hourly_stats["requests_1h"] or 0
    errors_1h = hourly_stats["errors_1h"] or 0
    error_rate_1h = round((errors_1h / requests_1h * 100) if requests_1h > 0 else 0, 2)

    return {
        "api_keys": {
            "total": api_keys_stats["total_keys"] or 0,
            "active": api_keys_stats["active_keys"] or 0,
            "disabled": api_keys_stats["disabled_keys"] or 0,
            "revoked": api_keys_stats["revoked_keys"] or 0,
            "total_requests_all_time": api_keys_stats["total_requests_all_time"] or 0
        },
        "requests": {
            "last_24h": logs_stats["requests_24h"] or 0,
            "errors_24h": logs_stats["errors_24h"] or 0,
            "avg_latency_ms_24h": float(logs_stats["avg_latency_24h"] or 0),
            "last_1h": requests_1h,
            "errors_1h": errors_1h,
            "error_rate_1h_percent": error_rate_1h
        },
        "database": {
            "size_bytes": db_size["size_bytes"],
            "size_mb": round(db_size["size_bytes"] / (1024 * 1024), 2),
            "tables": [
                {
                    "name": t["table_name"],
                    "size_bytes": t["size_bytes"],
                    "size_mb": round(t["size_bytes"] / (1024 * 1024), 2),
                    "rows": t["row_count"]
                }
                for t in table_sizes
            ]
        },
        "alerts": {
            "high_error_rate": error_rate_1h > 5,
            "error_rate_threshold": 5
        },
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


@router.get("/system/error-rate")
async def get_error_rate(
    hours: int = Query(default=1, ge=1, le=24),
    admin_email: str = Depends(verify_google_token)
):
    """Get error rate for the last N hours with breakdown by endpoint."""
    pool = await get_admin_db_pool()
    if not pool:
        raise HTTPException(status_code=503, detail="Database not available")

    async with pool.acquire() as conn:
        # Overall stats
        overall = await conn.fetchrow(f"""
            SELECT
                COUNT(*) as total_requests,
                COUNT(*) FILTER (WHERE status_code >= 400) as error_requests,
                COUNT(*) FILTER (WHERE status_code >= 500) as server_errors,
                COUNT(*) FILTER (WHERE status_code >= 400 AND status_code < 500) as client_errors
            FROM admin_request_logs
            WHERE created_at > NOW() - INTERVAL '{hours} hours'
        """)

        # Breakdown by endpoint
        by_endpoint = await conn.fetch(f"""
            SELECT
                endpoint,
                COUNT(*) as total_requests,
                COUNT(*) FILTER (WHERE status_code >= 400) as errors,
                ROUND(AVG(latency_ms)::numeric, 2) as avg_latency
            FROM admin_request_logs
            WHERE created_at > NOW() - INTERVAL '{hours} hours'
            GROUP BY endpoint
            ORDER BY errors DESC
            LIMIT 10
        """)

        # Recent errors
        recent_errors = await conn.fetch(f"""
            SELECT endpoint, status_code, error_message, created_at
            FROM admin_request_logs
            WHERE created_at > NOW() - INTERVAL '{hours} hours'
            AND status_code >= 400
            ORDER BY created_at DESC
            LIMIT 20
        """)

    total = overall["total_requests"] or 0
    errors = overall["error_requests"] or 0
    error_rate = round((errors / total * 100) if total > 0 else 0, 2)

    return {
        "period_hours": hours,
        "total_requests": total,
        "error_requests": errors,
        "server_errors": overall["server_errors"] or 0,
        "client_errors": overall["client_errors"] or 0,
        "error_rate_percent": error_rate,
        "is_critical": error_rate > 5,
        "by_endpoint": [
            {
                "endpoint": e["endpoint"],
                "total": e["total_requests"],
                "errors": e["errors"],
                "error_rate": round((e["errors"] / e["total_requests"] * 100) if e["total_requests"] > 0 else 0, 2),
                "avg_latency_ms": float(e["avg_latency"] or 0)
            }
            for e in by_endpoint
        ],
        "recent_errors": [
            {
                "endpoint": e["endpoint"],
                "status_code": e["status_code"],
                "message": e["error_message"],
                "timestamp": e["created_at"].isoformat() if e["created_at"] else None
            }
            for e in recent_errors
        ],
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


@router.post("/system/cleanup")
async def trigger_cleanup(admin_email: str = Depends(verify_google_token)):
    """Manually trigger cleanup of old request logs."""
    pool = await get_admin_db_pool()
    if not pool:
        raise HTTPException(status_code=503, detail="Database not available")

    async with pool.acquire() as conn:
        deleted = await conn.fetchval("SELECT cleanup_old_request_logs()")

    return {
        "status": "success",
        "deleted_rows": deleted or 0,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


@router.post("/system/aggregate-usage")
async def trigger_usage_aggregation(
    date: Optional[str] = Query(default=None, description="Date to aggregate (YYYY-MM-DD), defaults to today"),
    admin_email: str = Depends(verify_google_token)
):
    """Manually trigger daily usage aggregation."""
    pool = await get_admin_db_pool()
    if not pool:
        raise HTTPException(status_code=503, detail="Database not available")

    try:
        if date:
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
        else:
            target_date = datetime.utcnow().date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    async with pool.acquire() as conn:
        await conn.execute("SELECT aggregate_daily_usage($1)", target_date)

    return {
        "status": "success",
        "aggregated_date": target_date.isoformat(),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


# ============================================
# LEADS MANAGEMENT
# ============================================

@router.get("/leads", response_model=dict)
async def get_leads(
    source: Optional[str] = Query(default=None, description="Filter by source (api_key_request, contact_form, newsletter)"),
    status: Optional[str] = Query(default=None, description="Filter by status (new, contacted, qualified, converted, lost)"),
    is_high_value: Optional[bool] = Query(default=None, description="Filter by high value flag"),
    search: Optional[str] = Query(default=None, description="Search by name, email, or company"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    admin_email: str = Depends(verify_google_token)
):
    """Get all leads with filters."""
    pool = await get_admin_db_pool()
    if not pool:
        raise HTTPException(status_code=503, detail="Database not available")

    # Build query dynamically
    where_clauses = []
    params = []
    param_num = 1

    if source:
        where_clauses.append(f"source = ${param_num}")
        params.append(source)
        param_num += 1

    if status:
        where_clauses.append(f"status = ${param_num}")
        params.append(status)
        param_num += 1

    if is_high_value is not None:
        where_clauses.append(f"is_high_value = ${param_num}")
        params.append(is_high_value)
        param_num += 1

    if search:
        where_clauses.append(f"(name ILIKE ${param_num} OR email ILIKE ${param_num} OR company ILIKE ${param_num})")
        params.append(f"%{search}%")
        param_num += 1

    where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    async with pool.acquire() as conn:
        # Get total count
        count_query = f"SELECT COUNT(*) FROM leads {where_sql}"
        total = await conn.fetchval(count_query, *params) or 0

        # Get leads
        params.extend([limit, offset])
        query = f"""
            SELECT
                id, source, name, email, company,
                use_case, subject, expected_volume,
                is_high_value, priority, status,
                created_at, contacted_at, internal_notes
            FROM leads
            {where_sql}
            ORDER BY created_at DESC
            LIMIT ${param_num} OFFSET ${param_num + 1}
        """
        rows = await conn.fetch(query, *params)

    leads = [
        LeadInfo(
            id=row["id"],
            source=row["source"],
            name=row["name"],
            email=row["email"],
            company=row["company"],
            use_case=row["use_case"],
            subject=row["subject"],
            expected_volume=row["expected_volume"],
            is_high_value=row["is_high_value"] or False,
            priority=row["priority"] or "normal",
            status=row["status"] or "new",
            created_at=row["created_at"],
            contacted_at=row["contacted_at"],
            internal_notes=row["internal_notes"]
        )
        for row in rows
    ]

    return {
        "leads": [lead.model_dump() for lead in leads],
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/leads/stats", response_model=LeadStats)
async def get_lead_stats(admin_email: str = Depends(verify_google_token)):
    """Get lead statistics."""
    pool = await get_admin_db_pool()
    if not pool:
        raise HTTPException(status_code=503, detail="Database not available")

    async with pool.acquire() as conn:
        stats = await conn.fetchrow(
            """
            SELECT
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE status = 'new') as new,
                COUNT(*) FILTER (WHERE is_high_value = true) as high_value,
                COUNT(*) FILTER (WHERE source = 'api_key_request') as api_requests,
                COUNT(*) FILTER (WHERE source = 'contact_form') as contacts,
                COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '7 days') as this_week,
                COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '30 days') as this_month
            FROM leads
            """
        )

    return LeadStats(
        total=stats["total"] or 0,
        new=stats["new"] or 0,
        high_value=stats["high_value"] or 0,
        api_requests=stats["api_requests"] or 0,
        contacts=stats["contacts"] or 0,
        this_week=stats["this_week"] or 0,
        this_month=stats["this_month"] or 0
    )


@router.patch("/leads/{lead_id}")
async def update_lead(
    lead_id: int,
    request: UpdateLeadRequest,
    admin_email: str = Depends(verify_google_token)
):
    """Update a lead (status, priority, assigned_to, notes)."""
    pool = await get_admin_db_pool()
    if not pool:
        raise HTTPException(status_code=503, detail="Database not available")

    updates = []
    params = []
    param_num = 1

    if request.status:
        updates.append(f"status = ${param_num}")
        params.append(request.status)
        param_num += 1

        if request.status == 'contacted':
            updates.append("contacted_at = NOW()")

    if request.priority:
        updates.append(f"priority = ${param_num}")
        params.append(request.priority)
        param_num += 1

    if request.assigned_to:
        updates.append(f"assigned_to = ${param_num}")
        params.append(request.assigned_to)
        param_num += 1

    if request.internal_notes is not None:
        updates.append(f"internal_notes = ${param_num}")
        params.append(request.internal_notes)
        param_num += 1

    if not updates:
        raise HTTPException(status_code=400, detail="No updates provided")

    updates.append("updated_at = NOW()")
    params.append(lead_id)

    query = f"UPDATE leads SET {', '.join(updates)} WHERE id = ${param_num}"

    async with pool.acquire() as conn:
        result = await conn.execute(query, *params)
        if result == "UPDATE 0":
            raise HTTPException(status_code=404, detail="Lead not found")

    return {"success": True, "message": "Lead updated successfully"}


@router.get("/leads/export")
async def export_leads(
    source: Optional[str] = Query(default=None, description="Filter by source"),
    admin_email: str = Depends(verify_google_token)
):
    """Export leads to CSV."""
    pool = await get_admin_db_pool()
    if not pool:
        raise HTTPException(status_code=503, detail="Database not available")

    where_sql = ""
    params = []
    if source:
        where_sql = "WHERE source = $1"
        params = [source]

    async with pool.acquire() as conn:
        query = f"""
            SELECT
                created_at, source, name, email, company,
                use_case, subject, expected_volume,
                is_high_value, priority, status, contacted_at
            FROM leads
            {where_sql}
            ORDER BY created_at DESC
        """
        rows = await conn.fetch(query, *params) if params else await conn.fetch(query)

    # Convert to CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Created At", "Source", "Name", "Email", "Company",
        "Use Case", "Subject", "Expected Volume",
        "High Value", "Priority", "Status", "Contacted At"
    ])

    for row in rows:
        writer.writerow([
            row["created_at"].isoformat() if row["created_at"] else "",
            row["source"] or "",
            row["name"] or "",
            row["email"] or "",
            row["company"] or "",
            row["use_case"] or "",
            row["subject"] or "",
            row["expected_volume"] or "",
            "Yes" if row["is_high_value"] else "No",
            row["priority"] or "",
            row["status"] or "",
            row["contacted_at"].isoformat() if row["contacted_at"] else ""
        ])

    output.seek(0)
    filename = f"leads-{datetime.utcnow().strftime('%Y%m%d')}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

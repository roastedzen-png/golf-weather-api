"""
Golf Weather Physics API

A B2B REST API that calculates how weather conditions affect golf ball flight.
Production-ready with authentication, rate limiting, and usage tracking.
"""

from contextlib import asynccontextmanager
from datetime import datetime
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import sentry_sdk

from app.config import settings
from app.database import init_db, close_db
from app.redis_client import init_redis, close_redis
from app.routers import trajectory, conditions, health, admin
from app.middleware.authentication import AuthMiddleware
from app.middleware.rate_limiting import RateLimitMiddleware
from app.middleware.errors import setup_exception_handlers
from app.middleware.logging_config import setup_logging, logger


# Initialize Sentry if configured
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        traces_sample_rate=0.1 if settings.ENVIRONMENT == "production" else 1.0,
        profiles_sample_rate=0.1 if settings.ENVIRONMENT == "production" else 1.0,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Setup logging
    setup_logging()

    # Startup
    logger.info(
        "Starting Golf Weather API",
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
    )

    # Initialize database
    try:
        await init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.warning("Database not available", error=str(e))

    # Initialize Redis
    try:
        await init_redis()
        logger.info("Redis connection verified")
    except Exception as e:
        logger.warning("Redis not available", error=str(e))

    yield

    # Shutdown
    logger.info("Shutting down Golf Weather API")
    await close_redis()
    await close_db()


# Determine if we should show docs
show_docs = settings.ENVIRONMENT != "production"

app = FastAPI(
    title="Golf Weather Physics API",
    description=(
        "Calculate how weather conditions affect golf ball flight. "
        "Send shot data and weather conditions, receive adjusted trajectory "
        "and impact breakdown."
    ),
    version=settings.VERSION,
    docs_url="/docs" if show_docs else None,
    redoc_url="/redoc" if show_docs else None,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware (order matters: auth runs first, then rate limiting)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(AuthMiddleware)

# Setup error handlers
setup_exception_handlers(app)


# Request ID and logging middleware
@app.middleware("http")
async def add_request_context(request: Request, call_next):
    """Add request ID and log all requests."""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    start_time = time.time()

    response = await call_next(request)

    # Add headers
    response.headers["X-Request-ID"] = request_id
    response.headers["X-API-Version"] = settings.VERSION

    # Log request
    latency_ms = (time.time() - start_time) * 1000
    client_id = getattr(request.state, "client_id", "anonymous")

    logger.info(
        "Request completed",
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        latency_ms=round(latency_ms, 2),
        client=client_id,
    )

    return response


# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(trajectory.router, prefix="/api/v1", tags=["Trajectory"])
app.include_router(conditions.router, prefix="/api/v1", tags=["Conditions"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])

# Legacy routes (for backwards compatibility)
app.include_router(trajectory.router, prefix="/v1", tags=["Trajectory (Legacy)"])
app.include_router(conditions.router, prefix="/v1", tags=["Conditions (Legacy)"])


@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Golf Weather Physics API",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs" if show_docs else "disabled",
        "health": "/api/v1/health",
    }


# Legacy health endpoint for backwards compatibility
@app.get("/v1/health", include_in_schema=False)
async def legacy_health():
    """Legacy health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

"""
Golf Weather Physics API

A B2B REST API that calculates how weather conditions affect golf ball flight.
"""

from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import trajectory, conditions
from app.models.responses import HealthResponse
from app.config import settings


app = FastAPI(
    title="Golf Weather Physics API",
    description=(
        "Calculate how weather conditions affect golf ball flight. "
        "Send shot data and weather conditions, receive adjusted trajectory "
        "and impact breakdown."
    ),
    version=settings.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(trajectory.router, prefix="/v1", tags=["Trajectory"])
app.include_router(conditions.router, prefix="/v1", tags=["Conditions"])


@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint redirects to docs."""
    return {
        "message": "Golf Weather Physics API",
        "docs": "/docs",
        "health": "/v1/health",
    }


@app.get("/v1/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """
    Health check endpoint.

    Returns the API status, version, and current timestamp.
    Use this endpoint to verify the API is running and responsive.
    """
    return HealthResponse(
        status="healthy",
        version=settings.API_VERSION,
        timestamp=datetime.utcnow(),
    )

"""
Database Models for Usage Tracking

SQLAlchemy models for API usage statistics.
"""

from sqlalchemy import Column, Integer, String, DateTime, Date, Float, Boolean, Index
from sqlalchemy.sql import func
from app.database import Base


class APIUsage(Base):
    """Daily aggregated API usage statistics per client."""

    __tablename__ = "api_usage"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String(50), nullable=False, index=True)
    endpoint = Column(String(100), nullable=False)
    date = Column(Date, nullable=False, index=True)
    request_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    total_latency_ms = Column(Float, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index("ix_usage_client_date", "client_id", "date"),
        Index("ix_usage_client_endpoint_date", "client_id", "endpoint", "date", unique=True),
    )


class APIKey(Base):
    """API key storage with hashed keys."""

    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String(50), unique=True, nullable=False, index=True)
    key_hash = Column(String(64), nullable=False)  # SHA256 hash
    tier = Column(String(20), default="standard")  # free, standard, professional, enterprise
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used_at = Column(DateTime(timezone=True))


class RequestLog(Base):
    """Individual request logs for detailed analysis."""

    __tablename__ = "request_logs"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String(36), unique=True, nullable=False, index=True)
    client_id = Column(String(50), nullable=False, index=True)
    endpoint = Column(String(100), nullable=False)
    method = Column(String(10), nullable=False)
    status_code = Column(Integer, nullable=False)
    latency_ms = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    __table_args__ = (Index("ix_logs_client_created", "client_id", "created_at"),)

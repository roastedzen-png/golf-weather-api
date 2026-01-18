"""
Database Models for Usage Tracking and Lead Management

SQLAlchemy models for API usage statistics and lead management.
"""

from sqlalchemy import Column, Integer, String, DateTime, Date, Float, Boolean, Index, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
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

    # Lead capture data
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True, index=True)
    company = Column(String(255), nullable=True)
    use_case = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    expected_volume = Column(String(50), nullable=True)
    status = Column(String(20), default="active")  # active, revoked, expired

    # Relationship to leads
    leads = relationship("Lead", back_populates="api_key")


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


class Lead(Base):
    """Lead management for API key requests and contact form submissions."""

    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)

    # Lead Source
    source = Column(String(50), nullable=False, index=True)  # 'api_key_request', 'contact_form', 'newsletter'

    # Contact Information
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=True)

    # API Key Request Specific
    use_case = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    expected_volume = Column(String(50), nullable=True)
    api_key_id = Column(Integer, ForeignKey('api_keys.id'), nullable=True)

    # Contact Form Specific
    subject = Column(String(500), nullable=True)
    message = Column(Text, nullable=True)

    # Lead Quality
    is_high_value = Column(Boolean, default=False, index=True)
    priority = Column(String(20), default='normal')  # 'low', 'normal', 'high', 'urgent'

    # Status Tracking
    status = Column(String(50), default='new', index=True)  # 'new', 'contacted', 'qualified', 'converted', 'lost'
    assigned_to = Column(String(255), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    contacted_at = Column(DateTime(timezone=True), nullable=True)

    # Notes
    internal_notes = Column(Text, nullable=True)

    # Metadata
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(Text, nullable=True)
    referrer = Column(String(500), nullable=True)

    # Relationship to API key
    api_key = relationship("APIKey", back_populates="leads")

    __table_args__ = (
        Index("ix_leads_source_status", "source", "status"),
    )

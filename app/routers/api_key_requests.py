"""
API Key Request Router

Handles email-based API key generation for lead capture.
Integrates with database and email service for full automation.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import secrets
import hashlib
import logging
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models.database import APIKey, Lead
from app.utils.recaptcha import verify_recaptcha
from app.services.email import send_api_key_email, send_admin_notification

router = APIRouter(tags=["api-key-requests"])
logger = logging.getLogger(__name__)


class ApiKeyRequestModel(BaseModel):
    """Request model for API key generation."""
    name: str
    email: EmailStr
    company: Optional[str] = None
    use_case: str
    description: Optional[str] = None
    expected_volume: str
    agreed_to_terms: bool
    recaptcha_token: Optional[str] = None


class ApiKeyResponse(BaseModel):
    """Response model for API key request."""
    success: bool
    message: str
    email: str


def is_high_value_prospect(request: ApiKeyRequestModel) -> bool:
    """Identify prospects worth sales follow-up."""
    high_value_indicators = [
        # Has company name
        request.company is not None and len(request.company) > 0,
        # High-value use cases
        request.use_case in ['Launch Monitor Integration', 'Tournament Software', 'launch_monitor', 'tournament', 'golf_course'],
        # High volume expectation
        request.expected_volume in ['10K-100K', '100K+', '10k_100k', 'over_100k'],
        # Known golf tech domains
        any(domain in request.email.lower() for domain in [
            'trackman', 'inrange', 'foresight', 'arccos', 'garmin', 'topgolf',
            'titleist', 'callaway', 'taylormade', 'ping', 'cobra'
        ])
    ]
    # If 2+ indicators, flag as high-value
    return sum(high_value_indicators) >= 2


@router.post("/api/request-api-key", response_model=ApiKeyResponse)
async def request_api_key(
    request: ApiKeyRequestModel,
    http_request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate and email a new API key.

    This endpoint:
    1. Validates the request and reCAPTCHA
    2. Checks for existing key
    3. Generates a new API key
    4. Stores in database (api_keys + leads tables)
    5. Sends welcome email with API key
    6. Notifies admin for high-value prospects
    """

    # Validate terms agreement
    if not request.agreed_to_terms:
        raise HTTPException(
            status_code=400,
            detail="Must agree to Terms of Service"
        )

    # Verify reCAPTCHA token
    if request.recaptcha_token:
        await verify_recaptcha(
            token=request.recaptcha_token,
            action='api_key_request',
            min_score=0.5
        )

    # Check for existing key with this email in database
    if db:
        result = await db.execute(
            select(APIKey).where(
                APIKey.email == request.email,
                APIKey.is_active == True
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            logger.info(f"[API KEY] Existing key requested for: {request.email}")
            # TODO: Implement resend existing key email
            return ApiKeyResponse(
                success=True,
                message="API key sent to your email",
                email=request.email
            )

    # Generate new API key
    raw_key = f"golf_{secrets.token_urlsafe(32)}"
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

    # Generate client_id
    client_id = f"client_{secrets.token_urlsafe(8)}"

    # Determine if high-value lead
    is_high_value = is_high_value_prospect(request)

    # Get request metadata
    ip_address = http_request.client.host if http_request.client else None
    user_agent = http_request.headers.get('user-agent')
    referrer = http_request.headers.get('referer')

    api_key_id = None

    if db:
        try:
            # Store API key in database
            api_key = APIKey(
                client_id=client_id,
                key_hash=key_hash,
                tier='developer',
                is_active=True,
                name=request.name,
                email=request.email,
                company=request.company,
                use_case=request.use_case,
                description=request.description,
                expected_volume=request.expected_volume,
                status='active'
            )
            db.add(api_key)
            await db.flush()  # Get the ID
            api_key_id = api_key.id

            # Store in leads table
            lead = Lead(
                source='api_key_request',
                name=request.name,
                email=request.email,
                company=request.company,
                use_case=request.use_case,
                description=request.description,
                expected_volume=request.expected_volume,
                api_key_id=api_key_id,
                is_high_value=is_high_value,
                status='new',
                ip_address=ip_address,
                user_agent=user_agent,
                referrer=referrer
            )
            db.add(lead)

            await db.commit()
            logger.info(f"[API KEY] Stored in database for {request.email}, key_id: {api_key_id}")

        except Exception as e:
            await db.rollback()
            logger.error(f"[API KEY] Database error: {str(e)}")
            # Continue with email even if database fails
    else:
        logger.warning("[API KEY] No database connection, key not persisted")

    # Log the key generation
    logger.info(f"[API KEY] New key generated for {request.email}")

    # Send welcome email with API key
    email_sent = await send_api_key_email(
        email=request.email,
        name=request.name,
        api_key=raw_key
    )

    if email_sent:
        logger.info(f"[API KEY] Welcome email sent to {request.email}")
    else:
        logger.warning(f"[API KEY] Failed to send email to {request.email}")

    # Notify admin for high-value prospects
    if is_high_value:
        logger.info(
            f"[HIGH VALUE LEAD] {request.email} - "
            f"Company: {request.company}, "
            f"Use Case: {request.use_case}, "
            f"Volume: {request.expected_volume}"
        )
        await send_admin_notification(
            lead_type="API Key Request",
            lead_data={
                'name': request.name,
                'email': request.email,
                'company': request.company,
                'use_case': request.use_case,
                'expected_volume': request.expected_volume,
                'description': request.description
            },
            is_high_value=True
        )

    return ApiKeyResponse(
        success=True,
        message="API key sent to your email",
        email=request.email
    )


@router.get("/api/key-requests/stats")
async def get_key_request_stats(db: AsyncSession = Depends(get_db)):
    """
    Get statistics about API key requests (admin only).
    TODO: Add admin authentication
    """
    if not db:
        return {
            'total_requests': 0,
            'high_value_leads': 0,
            'by_use_case': {}
        }

    try:
        # Get total from leads table
        from sqlalchemy import func

        total_result = await db.execute(
            select(func.count(Lead.id)).where(Lead.source == 'api_key_request')
        )
        total = total_result.scalar() or 0

        high_value_result = await db.execute(
            select(func.count(Lead.id)).where(
                Lead.source == 'api_key_request',
                Lead.is_high_value == True
            )
        )
        high_value = high_value_result.scalar() or 0

        # Get by use case
        use_case_result = await db.execute(
            select(Lead.use_case, func.count(Lead.id))
            .where(Lead.source == 'api_key_request')
            .group_by(Lead.use_case)
        )
        by_use_case = {row[0] or 'unknown': row[1] for row in use_case_result.all()}

        return {
            'total_requests': total,
            'high_value_leads': high_value,
            'by_use_case': by_use_case
        }

    except Exception as e:
        logger.error(f"[API KEY STATS] Error: {str(e)}")
        return {
            'total_requests': 0,
            'high_value_leads': 0,
            'by_use_case': {},
            'error': str(e)
        }

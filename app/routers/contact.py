"""
Contact Form Router

Handles contact form submissions with lead capture.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from typing import Optional

from app.database import get_db
from app.models.database import Lead
from app.utils.recaptcha import verify_recaptcha
from app.services.email import send_contact_confirmation, send_admin_notification

router = APIRouter(tags=["contact"])
logger = logging.getLogger(__name__)


class ContactRequest(BaseModel):
    """Request model for contact form."""
    name: str
    email: EmailStr
    company: Optional[str] = None
    subject: str
    message: str
    recaptcha_token: Optional[str] = None


class ContactResponse(BaseModel):
    """Response model for contact form."""
    success: bool
    message: str


def is_high_value_contact(request: ContactRequest) -> bool:
    """Identify high-value contact form submissions."""
    message_lower = request.message.lower()
    subject_lower = request.subject.lower()

    high_value_keywords = [
        'enterprise', 'multi-location', 'chain', 'partnership',
        '100k', '1m', 'million', 'large scale', 'bulk', 'volume',
        'trackman', 'inrange', 'foresight', 'arccos', 'garmin',
        'topgolf', 'pga', 'tour', 'professional', 'commercial'
    ]

    return any(keyword in message_lower or keyword in subject_lower for keyword in high_value_keywords)


@router.post("/api/contact", response_model=ContactResponse)
async def submit_contact_form(
    request: ContactRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Handle contact form submissions.

    This endpoint:
    1. Verifies reCAPTCHA
    2. Stores lead in database
    3. Sends confirmation email to user
    4. Notifies admin about the inquiry
    """

    # Verify reCAPTCHA token
    if request.recaptcha_token:
        await verify_recaptcha(
            token=request.recaptcha_token,
            action='contact_form',
            min_score=0.4  # More lenient for contact forms
        )

    # Determine if high-value contact
    is_high_value = is_high_value_contact(request)

    # Get request metadata
    ip_address = http_request.client.host if http_request.client else None
    user_agent = http_request.headers.get('user-agent')
    referrer = http_request.headers.get('referer')

    if db:
        try:
            # Store in leads table
            lead = Lead(
                source='contact_form',
                name=request.name,
                email=request.email,
                company=request.company,
                subject=request.subject,
                message=request.message,
                is_high_value=is_high_value,
                priority='high' if is_high_value else 'normal',
                status='new',
                ip_address=ip_address,
                user_agent=user_agent,
                referrer=referrer
            )
            db.add(lead)
            await db.commit()
            logger.info(f"[CONTACT] Stored lead for {request.email}")

        except Exception as e:
            await db.rollback()
            logger.error(f"[CONTACT] Database error: {str(e)}")
            # Continue with email even if database fails
    else:
        logger.warning("[CONTACT] No database connection, lead not persisted")

    # Send confirmation email to user
    confirmation_sent = await send_contact_confirmation(
        email=request.email,
        name=request.name,
        subject=request.subject
    )

    if confirmation_sent:
        logger.info(f"[CONTACT] Confirmation email sent to {request.email}")
    else:
        logger.warning(f"[CONTACT] Failed to send confirmation to {request.email}")

    # Notify admin about the inquiry
    await send_admin_notification(
        lead_type="Contact Form",
        lead_data={
            'name': request.name,
            'email': request.email,
            'company': request.company,
            'subject': request.subject,
            'message': request.message
        },
        is_high_value=is_high_value
    )

    if is_high_value:
        logger.info(f"[HIGH VALUE CONTACT] {request.email} - Subject: {request.subject}")

    return ContactResponse(
        success=True,
        message="Thanks for reaching out! We'll be in touch soon."
    )

"""
reCAPTCHA v3 Verification Utility

Verifies reCAPTCHA tokens to prevent spam on public forms.
"""

import os
import httpx
import logging
from fastapi import HTTPException

logger = logging.getLogger(__name__)

RECAPTCHA_SECRET_KEY = os.getenv('RECAPTCHA_SECRET_KEY')
RECAPTCHA_VERIFY_URL = 'https://www.google.com/recaptcha/api/siteverify'


async def verify_recaptcha(
    token: str,
    action: str,
    min_score: float = 0.5
) -> bool:
    """
    Verify reCAPTCHA v3 token.

    Args:
        token: reCAPTCHA token from frontend
        action: Expected action (e.g., 'api_key_request', 'contact_form')
        min_score: Minimum acceptable score (0.0-1.0), default 0.5

    Returns:
        True if verification passes

    Raises:
        HTTPException if verification fails

    Score interpretation:
        1.0: Definitely a human
        0.9-1.0: Very likely human
        0.7-0.9: Likely human
        0.5-0.7: Neutral
        0.3-0.5: Suspicious
        0.0-0.3: Likely bot
    """

    # Skip verification in development if no secret key
    if not RECAPTCHA_SECRET_KEY:
        environment = os.getenv('ENVIRONMENT', 'development')
        if environment == 'development':
            logger.warning("reCAPTCHA verification skipped (no secret key in development)")
            return True
        raise HTTPException(
            status_code=500,
            detail="reCAPTCHA not configured"
        )

    # Skip if no token provided (optional reCAPTCHA)
    if not token:
        logger.warning("No reCAPTCHA token provided")
        # In production, you might want to reject requests without tokens
        return True

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                RECAPTCHA_VERIFY_URL,
                data={
                    'secret': RECAPTCHA_SECRET_KEY,
                    'response': token
                },
                timeout=10.0
            )

            result = response.json()

            # Log result for monitoring
            logger.info(
                "reCAPTCHA verification",
                success=result.get('success'),
                score=result.get('score'),
                action=result.get('action'),
                expected_action=action
            )

            # Check if verification was successful
            if not result.get('success'):
                error_codes = result.get('error-codes', [])
                logger.warning(f"reCAPTCHA verification failed: {error_codes}")
                raise HTTPException(
                    status_code=400,
                    detail=f"reCAPTCHA verification failed: {error_codes}"
                )

            # Check action matches (optional, but recommended)
            if result.get('action') and result.get('action') != action:
                logger.warning(
                    f"reCAPTCHA action mismatch: expected {action}, got {result.get('action')}"
                )
                # Don't fail on action mismatch, just log it
                # raise HTTPException(status_code=400, detail="reCAPTCHA action mismatch")

            # Check score
            score = result.get('score', 0.0)
            if score < min_score:
                logger.warning(f"Low reCAPTCHA score: {score} for action: {action}")
                raise HTTPException(
                    status_code=429,
                    detail="Request flagged as potential spam"
                )

            return True

    except httpx.RequestError as e:
        logger.error(f"reCAPTCHA verification request failed: {e}")
        # In case of network error, allow the request in development
        environment = os.getenv('ENVIRONMENT', 'development')
        if environment == 'development':
            return True
        raise HTTPException(
            status_code=500,
            detail="reCAPTCHA verification unavailable"
        )


def get_recommended_threshold(action: str) -> float:
    """
    Get recommended reCAPTCHA threshold for different actions.

    Args:
        action: The action being performed

    Returns:
        Recommended minimum score threshold
    """
    thresholds = {
        'api_key_request': 0.5,  # Standard protection
        'contact_form': 0.4,     # More lenient
        'newsletter': 0.3,       # Most lenient
        'login': 0.3,            # Lenient to avoid blocking users
    }
    return thresholds.get(action, 0.5)

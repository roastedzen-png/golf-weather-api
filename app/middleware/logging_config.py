"""
Structured Logging Configuration

Sets up structlog for JSON logging in production.
"""

import logging
import sys
import structlog
from app.config import settings


def setup_logging():
    """Configure structured logging based on environment."""

    # Determine if we're in production
    is_production = settings.ENVIRONMENT == "production"

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL.upper()),
    )

    # Configure structlog
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    if is_production:
        # JSON output for production (easier to parse in log aggregators)
        processors.append(structlog.processors.JSONRenderer())
    else:
        # Pretty console output for development
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.LOG_LEVEL.upper())
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


# Create a logger instance
def get_logger(name: str = None):
    """Get a structlog logger instance."""
    return structlog.get_logger(name)


logger = get_logger("golf_api")

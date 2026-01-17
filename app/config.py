"""
Application Configuration

Loads settings from environment variables with sensible defaults.
"""

from pydantic_settings import BaseSettings
from typing import List, Dict
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    VERSION: str = "1.0.6"
    ENVIRONMENT: str = "development"  # development, staging, production
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = ""

    # Redis
    REDIS_URL: str = ""

    # API Keys (loaded separately)
    API_KEYS: Dict[str, str] = {}
    ADMIN_KEY_HASH: str = ""

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 1000
    RATE_LIMIT_BURST: int = 100

    # CORS
    CORS_ORIGINS: List[str] = [
        "https://app.inrangegolf.com",
        "https://admin.inrangegolf.com",
        "http://localhost:3000",
    ]

    # Weather API
    WEATHER_API_KEY: str = ""
    WEATHER_API_BASE_URL: str = "https://api.weatherapi.com/v1"

    # Sentry
    SENTRY_DSN: str = ""

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    def load_api_keys(self):
        """Load API keys from environment variables.

        Format: APIKEY_CLIENTNAME=hash
        Example: APIKEY_INRANGE_PROD=abc123...
        """
        for key, value in os.environ.items():
            if key.startswith("APIKEY_"):
                client_name = key.replace("APIKEY_", "").lower()
                self.API_KEYS[client_name] = value

    @property
    def api_version(self) -> str:
        """Backwards compatibility alias."""
        return self.VERSION

    @property
    def API_VERSION(self) -> str:
        """Backwards compatibility alias."""
        return self.VERSION


# Create settings instance
settings = Settings()
settings.load_api_keys()

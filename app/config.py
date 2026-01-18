"""
Application Configuration

Loads settings from environment variables with sensible defaults.
"""

from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

# Load .env file into os.environ BEFORE creating settings
load_dotenv()


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

    # Rate Limiting (legacy - kept for backwards compatibility)
    RATE_LIMIT_PER_MINUTE: int = 1000
    RATE_LIMIT_BURST: int = 100

    # CORS - stored as string, parsed by validator
    CORS_ORIGINS: str = "https://app.inrangegolf.com,https://admin.inrangegolf.com,http://localhost:3000"

    # Weather API
    WEATHER_API_KEY: str = ""
    WEATHER_API_BASE_URL: str = "https://api.weatherapi.com/v1"

    # Sentry
    SENTRY_DSN: str = ""

    # Logging
    LOG_LEVEL: str = "INFO"

    # Admin Dashboard (Google OAuth)
    GOOGLE_CLIENT_ID: str = ""
    ADMIN_EMAIL: str = "golfphysicsio@gmail.com"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS as comma-separated list."""
        if not self.CORS_ORIGINS:
            return []
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

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


# 5-Tier Rate Limits Configuration
RATE_LIMITS = {
    'developer': {
        'price_monthly': 0,
        'requests_per_minute': 60,
        'requests_per_day': 1000,
        'requests_per_month': 30000,
        'features': [
            'real_time_weather',
            'physics_calculations',
            'multi_unit_support',
            'api_documentation',
            'community_support'
        ],
        'excluded_features': [
            'historical_data',
            'forecasts',
            'analytics_dashboard',
            'sla',
            'phone_support'
        ]
    },
    'starter': {
        'price_monthly': 99,
        'requests_per_minute': 200,
        'requests_per_day': 10000,
        'requests_per_month': 300000,
        'features': [
            'real_time_weather',
            'physics_calculations',
            'multi_unit_support',
            'historical_data_30d',
            'forecasts_7d',
            'email_support_48h',
            'usage_analytics'
        ],
        'excluded_features': [
            'sla',
            'phone_support',
            'account_manager'
        ]
    },
    'professional': {
        'price_monthly': 299,
        'requests_per_minute': 500,
        'requests_per_day': 25000,
        'requests_per_month': 750000,
        'features': [
            'all_starter_features',
            'sla_999',
            'priority_email_24h',
            'phone_support',
            'historical_data_90d',
            'forecasts_14d',
            'advanced_analytics',
            'webhooks'
        ],
        'excluded_features': [
            'white_label',
            'account_manager',
            'on_premise'
        ]
    },
    'business': {
        'price_monthly': 599,
        'requests_per_minute': 2000,
        'requests_per_day': 100000,
        'requests_per_month': 3000000,
        'features': [
            'all_professional_features',
            'sla_9995',
            'priority_support_4h',
            'account_manager',
            'historical_data_1y',
            'custom_integration_help',
            'volume_discounts',
            'quarterly_reviews'
        ],
        'excluded_features': [
            'white_label',
            'on_premise'
        ]
    },
    'enterprise': {
        'price_monthly': 1999,  # Starting price
        'requests_per_minute': None,  # Unlimited
        'requests_per_day': None,  # Unlimited
        'requests_per_month': None,  # Unlimited
        'features': [
            'all_business_features',
            'sla_9999',
            'dedicated_engineer',
            'critical_response_1h',
            'white_label',
            'on_premise_deployment',
            'custom_features',
            'api_roadmap_input'
        ],
        'excluded_features': []
    }
}


# Volume pricing for Business tier
BUSINESS_VOLUME_PRICING = {
    '2-5': 599,
    '6-10': 999,
    '11-20': 1499,
    '20+': 'custom'
}

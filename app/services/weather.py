"""
Weather Service

Fetches current weather conditions from WeatherAPI.com
"""

from datetime import datetime
from typing import Optional

import httpx

from app.config import settings


WEATHER_API_BASE = "https://api.weatherapi.com/v1"


# City altitude lookup (feet above sea level)
# Expand as needed for better coverage
CITY_ALTITUDES = {
    ("phoenix", "az", "us"): 1086,
    ("denver", "co", "us"): 5280,
    ("scottsdale", "az", "us"): 1257,
    ("las vegas", "nv", "us"): 2001,
    ("los angeles", "ca", "us"): 285,
    ("miami", "fl", "us"): 6,
    ("new york", "ny", "us"): 33,
    ("chicago", "il", "us"): 594,
    ("atlanta", "ga", "us"): 1050,
    ("dallas", "tx", "us"): 430,
    ("seattle", "wa", "us"): 175,
    ("boston", "ma", "us"): 141,
    ("san francisco", "ca", "us"): 52,
    ("austin", "tx", "us"): 489,
    ("portland", "or", "us"): 50,
    ("salt lake city", "ut", "us"): 4226,
    ("albuquerque", "nm", "us"): 5312,
    ("tucson", "az", "us"): 2389,
    ("san diego", "ca", "us"): 62,
    ("orlando", "fl", "us"): 82,
    ("houston", "tx", "us"): 80,
    ("nashville", "tn", "us"): 597,
    ("charlotte", "nc", "us"): 751,
    ("minneapolis", "mn", "us"): 830,
    ("detroit", "mi", "us"): 600,
    ("philadelphia", "pa", "us"): 39,
    ("washington", "dc", "us"): 125,
    ("tampa", "fl", "us"): 48,
    ("raleigh", "nc", "us"): 315,
    ("indianapolis", "in", "us"): 715,
}


def get_city_altitude(
    city: str, state: Optional[str] = None, country: str = "US"
) -> float:
    """
    Get altitude for a city.

    Args:
        city: City name
        state: State or region (optional)
        country: Country code

    Returns:
        Altitude in feet, or 0 (sea level) if unknown
    """
    key = (
        city.lower().strip(),
        (state.lower().strip() if state else ""),
        (country.lower().strip() if country else "us"),
    )
    return CITY_ALTITUDES.get(key, 0)


async def fetch_weather_by_city(
    city: str, state: Optional[str] = None, country: str = "US"
) -> dict:
    """
    Fetch current weather from WeatherAPI.com

    Args:
        city: City name
        state: State or region (optional)
        country: Country code

    Returns:
        Dictionary with weather conditions

    Raises:
        httpx.HTTPStatusError: If API request fails
        ValueError: If API key is not configured
    """
    if not settings.WEATHER_API_KEY:
        raise ValueError("WEATHER_API_KEY is not configured")

    # Build location query string
    location_parts = [city]
    if state:
        location_parts.append(state)
    if country:
        location_parts.append(country)
    location = ",".join(location_parts)

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{WEATHER_API_BASE}/current.json",
            params={
                "key": settings.WEATHER_API_KEY,
                "q": location,
                "aqi": "no",
            },
            timeout=10.0,
        )
        response.raise_for_status()
        data = response.json()

    current = data["current"]
    location_data = data["location"]

    # Get altitude (WeatherAPI doesn't provide elevation)
    altitude_ft = get_city_altitude(city, state, country)

    # Build formatted location string
    location_str = location_data["name"]
    if location_data.get("region"):
        location_str += f", {location_data['region']}"
    if location_data.get("country"):
        location_str += f", {location_data['country']}"

    return {
        "location": location_str,
        "wind_speed_mph": current["wind_mph"],
        "wind_direction_deg": current["wind_degree"],
        "temperature_f": current["temp_f"],
        "altitude_ft": altitude_ft,
        "humidity_pct": current["humidity"],
        "pressure_inhg": current["pressure_in"],
        "conditions_text": current["condition"]["text"],
        "fetched_at": datetime.utcnow(),
    }


async def fetch_weather_by_coords(lat: float, lon: float) -> dict:
    """
    Fetch current weather by coordinates.

    Args:
        lat: Latitude
        lon: Longitude

    Returns:
        Dictionary with weather conditions
    """
    if not settings.WEATHER_API_KEY:
        raise ValueError("WEATHER_API_KEY is not configured")

    location = f"{lat},{lon}"

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{WEATHER_API_BASE}/current.json",
            params={
                "key": settings.WEATHER_API_KEY,
                "q": location,
                "aqi": "no",
            },
            timeout=10.0,
        )
        response.raise_for_status()
        data = response.json()

    current = data["current"]
    location_data = data["location"]

    # Build formatted location string
    location_str = location_data["name"]
    if location_data.get("region"):
        location_str += f", {location_data['region']}"
    if location_data.get("country"):
        location_str += f", {location_data['country']}"

    return {
        "location": location_str,
        "wind_speed_mph": current["wind_mph"],
        "wind_direction_deg": current["wind_degree"],
        "temperature_f": current["temp_f"],
        "altitude_ft": 0,  # Would need elevation API for accurate altitude
        "humidity_pct": current["humidity"],
        "pressure_inhg": current["pressure_in"],
        "conditions_text": current["condition"]["text"],
        "fetched_at": datetime.utcnow(),
    }

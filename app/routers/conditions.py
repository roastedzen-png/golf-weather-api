"""
Conditions Router

Endpoints for fetching weather conditions without trajectory calculation.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.models.responses import ConditionsResponse
from app.services.weather import fetch_weather_by_city, fetch_weather_by_coords


router = APIRouter()


@router.get("/conditions", response_model=ConditionsResponse)
async def get_conditions(
    city: str = Query(..., min_length=1, description="City name"),
    state: Optional[str] = Query(default=None, description="State or region"),
    country: Optional[str] = Query(default="US", description="Country code"),
) -> ConditionsResponse:
    """
    Fetch current weather conditions for a location.

    This utility endpoint returns current weather conditions without
    performing any trajectory calculations. Useful for displaying
    conditions to users or caching weather data.
    """
    try:
        weather = await fetch_weather_by_city(
            city=city,
            state=state,
            country=country,
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to fetch weather data: {str(e)}",
        )

    return ConditionsResponse(
        location=weather["location"],
        wind_speed_mph=weather["wind_speed_mph"],
        wind_direction_deg=weather["wind_direction_deg"],
        temperature_f=weather["temperature_f"],
        altitude_ft=weather["altitude_ft"],
        humidity_pct=weather["humidity_pct"],
        pressure_inhg=weather["pressure_inhg"],
        conditions_text=weather["conditions_text"],
        fetched_at=weather["fetched_at"],
    )


@router.get("/conditions/coords", response_model=ConditionsResponse)
async def get_conditions_by_coords(
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
) -> ConditionsResponse:
    """
    Fetch current weather conditions by GPS coordinates.

    This endpoint returns current weather conditions for a given latitude
    and longitude. Useful for geolocation-based weather lookup.
    """
    try:
        weather = await fetch_weather_by_coords(lat=lat, lon=lon)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to fetch weather data: {str(e)}",
        )

    return ConditionsResponse(
        location=weather["location"],
        wind_speed_mph=weather["wind_speed_mph"],
        wind_direction_deg=weather["wind_direction_deg"],
        temperature_f=weather["temperature_f"],
        altitude_ft=weather["altitude_ft"],
        humidity_pct=weather["humidity_pct"],
        pressure_inhg=weather["pressure_inhg"],
        conditions_text=weather["conditions_text"],
        fetched_at=weather["fetched_at"],
    )

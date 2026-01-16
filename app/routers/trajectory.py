"""
Trajectory Router

Endpoints for calculating golf ball trajectory with weather effects.
"""

from fastapi import APIRouter, HTTPException

from app.models.requests import (
    TrajectoryRequest,
    TrajectoryLocationRequest,
    TrajectoryCourseRequest,
    WeatherConditions,
)
from app.models.responses import (
    TrajectoryResponse,
    AdjustedResults,
    ImpactBreakdown,
    TrajectoryPoint,
    ConditionsUsed,
)
from app.services.physics import calculate_impact_breakdown
from app.services.weather import fetch_weather_by_city
from app.services.courses import get_course_location


router = APIRouter()


def build_trajectory_response(
    physics_result: dict, conditions_used: ConditionsUsed = None
) -> TrajectoryResponse:
    """Build a TrajectoryResponse from physics calculation results."""
    baseline = physics_result["baseline"]
    adjusted = physics_result["adjusted"]
    breakdown = physics_result["impact_breakdown"]

    return TrajectoryResponse(
        adjusted=AdjustedResults(
            carry_yards=adjusted["carry_yards"],
            total_yards=adjusted["total_yards"],
            lateral_drift_yards=adjusted["lateral_drift_yards"],
            apex_height_yards=adjusted["apex_height_yards"],
            flight_time_seconds=adjusted["flight_time_seconds"],
            landing_angle_deg=adjusted["landing_angle_deg"],
        ),
        baseline=AdjustedResults(
            carry_yards=baseline["carry_yards"],
            total_yards=baseline["total_yards"],
            lateral_drift_yards=baseline["lateral_drift_yards"],
            apex_height_yards=baseline["apex_height_yards"],
            flight_time_seconds=baseline["flight_time_seconds"],
            landing_angle_deg=baseline["landing_angle_deg"],
        ),
        impact_breakdown=ImpactBreakdown(
            wind_effect_yards=breakdown["wind_effect_yards"],
            wind_lateral_yards=breakdown["wind_lateral_yards"],
            temperature_effect_yards=breakdown["temperature_effect_yards"],
            altitude_effect_yards=breakdown["altitude_effect_yards"],
            humidity_effect_yards=breakdown["humidity_effect_yards"],
            total_adjustment_yards=breakdown["total_adjustment_yards"],
        ),
        equivalent_calm_distance_yards=physics_result["equivalent_calm_distance_yards"],
        trajectory_points=[
            TrajectoryPoint(x=p["x"], y=p["y"], z=p["z"])
            for p in adjusted["trajectory_points"]
        ],
        conditions_used=conditions_used,
    )


@router.post("/trajectory", response_model=TrajectoryResponse)
async def calculate_trajectory(request: TrajectoryRequest) -> TrajectoryResponse:
    """
    Calculate golf ball trajectory with manually provided weather conditions.

    This endpoint performs physics calculations to determine how weather
    conditions affect golf ball flight, including:
    - Wind effects (headwind/tailwind and crosswind)
    - Air density effects from temperature, altitude, humidity, and pressure
    - Spin effects (backspin lift and sidespin curve)

    Returns adjusted trajectory, baseline comparison, and impact breakdown.
    """
    result = calculate_impact_breakdown(request.shot, request.conditions)
    return build_trajectory_response(result)


@router.post("/trajectory/location", response_model=TrajectoryResponse)
async def calculate_trajectory_by_location(
    request: TrajectoryLocationRequest,
) -> TrajectoryResponse:
    """
    Calculate golf ball trajectory with weather fetched by city location.

    Automatically fetches current weather conditions for the specified city
    and calculates the trajectory with those conditions.
    """
    try:
        weather = await fetch_weather_by_city(
            city=request.location.city,
            state=request.location.state,
            country=request.location.country,
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to fetch weather data: {str(e)}",
        )

    # Build conditions from weather data
    conditions = WeatherConditions(
        wind_speed_mph=weather["wind_speed_mph"],
        wind_direction_deg=weather["wind_direction_deg"],
        temperature_f=weather["temperature_f"],
        altitude_ft=weather["altitude_ft"],
        humidity_pct=weather["humidity_pct"],
        pressure_inhg=weather["pressure_inhg"],
    )

    result = calculate_impact_breakdown(request.shot, conditions)

    conditions_used = ConditionsUsed(
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

    return build_trajectory_response(result, conditions_used)


@router.post("/trajectory/course", response_model=TrajectoryResponse)
async def calculate_trajectory_by_course(
    request: TrajectoryCourseRequest,
) -> TrajectoryResponse:
    """
    Calculate golf ball trajectory with weather fetched by golf course name.

    Looks up the course location and fetches current weather conditions
    for that location.
    """
    # Look up course
    course_data = get_course_location(request.course.name)
    if not course_data:
        raise HTTPException(
            status_code=404,
            detail=f"Course '{request.course.name}' not found. "
            "Try a well-known course name like 'TPC Scottsdale' or 'Pebble Beach'.",
        )

    try:
        weather = await fetch_weather_by_city(
            city=course_data["city"],
            state=course_data["state"],
            country=course_data["country"],
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to fetch weather data: {str(e)}",
        )

    # Use course's known altitude if available (more accurate than city lookup)
    altitude_ft = course_data.get("altitude_ft", weather["altitude_ft"])

    # Build conditions from weather data
    conditions = WeatherConditions(
        wind_speed_mph=weather["wind_speed_mph"],
        wind_direction_deg=weather["wind_direction_deg"],
        temperature_f=weather["temperature_f"],
        altitude_ft=altitude_ft,
        humidity_pct=weather["humidity_pct"],
        pressure_inhg=weather["pressure_inhg"],
    )

    result = calculate_impact_breakdown(request.shot, conditions)

    conditions_used = ConditionsUsed(
        location=weather["location"],
        wind_speed_mph=weather["wind_speed_mph"],
        wind_direction_deg=weather["wind_direction_deg"],
        temperature_f=weather["temperature_f"],
        altitude_ft=altitude_ft,
        humidity_pct=weather["humidity_pct"],
        pressure_inhg=weather["pressure_inhg"],
        conditions_text=weather["conditions_text"],
        fetched_at=weather["fetched_at"],
    )

    return build_trajectory_response(result, conditions_used)

from pydantic import BaseModel, Field
from typing import Optional


class ShotData(BaseModel):
    ball_speed_mph: float = Field(
        ..., gt=0, le=220, description="Ball speed in mph"
    )
    launch_angle_deg: float = Field(
        ..., ge=-10, le=60, description="Launch angle in degrees"
    )
    spin_rate_rpm: float = Field(
        ..., ge=0, le=15000, description="Total spin rate in RPM"
    )
    spin_axis_deg: float = Field(
        default=0,
        ge=-90,
        le=90,
        description="Spin axis tilt in degrees (negative = draw, positive = fade)",
    )
    direction_deg: float = Field(
        default=0,
        ge=-45,
        le=45,
        description="Initial direction relative to target line",
    )


class WeatherConditions(BaseModel):
    wind_speed_mph: float = Field(
        default=0, ge=0, le=60, description="Wind speed in mph"
    )
    wind_direction_deg: float = Field(
        default=0,
        ge=0,
        lt=360,
        description="Wind direction in degrees (0=headwind, 90=left-to-right, 180=tailwind, 270=right-to-left)",
    )
    temperature_f: float = Field(
        default=70, ge=-20, le=120, description="Temperature in Fahrenheit"
    )
    altitude_ft: float = Field(
        default=0, ge=-500, le=12000, description="Altitude in feet"
    )
    humidity_pct: float = Field(
        default=50, ge=0, le=100, description="Relative humidity percentage"
    )
    pressure_inhg: float = Field(
        default=29.92,
        ge=18,  # Allow low pressure for high altitudes (e.g., ~19 inHg at 12,000 ft)
        le=32,
        description="Barometric pressure in inches of mercury",
    )


class LocationQuery(BaseModel):
    city: str = Field(..., min_length=1, description="City name")
    state: Optional[str] = Field(default=None, description="State or region")
    country: str = Field(default="US", description="Country code")


class CourseQuery(BaseModel):
    name: str = Field(..., min_length=1, description="Golf course name")


class TrajectoryRequest(BaseModel):
    shot: ShotData
    conditions: WeatherConditions


class TrajectoryLocationRequest(BaseModel):
    shot: ShotData
    location: LocationQuery


class TrajectoryCourseRequest(BaseModel):
    shot: ShotData
    course: CourseQuery

from pydantic import BaseModel, Field, model_validator
from typing import Optional, Literal


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
        default=0, ge=0, le=150,
        description="Wind speed in mph (extended range 0-150 for gaming)"
    )
    wind_direction_deg: float = Field(
        default=0,
        ge=0,
        le=360,
        description="Wind direction in degrees (0=headwind, 90=left-to-right, 180=tailwind, 270=right-to-left)",
    )
    temperature_f: float = Field(
        default=70, ge=-40, le=130,
        description="Temperature in Fahrenheit (extended range -40 to 130 for gaming)"
    )
    altitude_ft: float = Field(
        default=0, ge=-500, le=15000,
        description="Altitude in feet (extended range for high altitude gaming)"
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


class CoordinateLocation(BaseModel):
    """GPS coordinates for weather lookup."""
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lng: float = Field(..., ge=-180, le=180, description="Longitude")


class ConditionsOverride(BaseModel):
    """
    Custom weather conditions for gaming scenarios.
    Extended ranges beyond normal weather to support entertainment gaming.
    """
    wind_speed: float = Field(
        ..., ge=0, le=150,
        description="Wind speed in mph (extended range for gaming: 0-150)"
    )
    wind_direction: float = Field(
        ..., ge=0, le=360,
        description="Wind direction in degrees (0=North/headwind, 90=East, 180=South/tailwind, 270=West)"
    )
    temperature: float = Field(
        ..., ge=-40, le=130,
        description="Temperature in Fahrenheit (extended range for gaming: -40 to 130)"
    )
    humidity: float = Field(
        ..., ge=0, le=100,
        description="Relative humidity percentage (0-100)"
    )
    altitude: float = Field(
        ..., ge=-100, le=15000,
        description="Altitude in feet (extended range for gaming: -100 to 15000)"
    )
    air_pressure: float = Field(
        ..., ge=25, le=32,
        description="Barometric pressure in inches of mercury (25-32)"
    )


class CalculateRequest(BaseModel):
    """
    Professional trajectory calculation request.

    Supports:
    - GPS coordinate-based weather (location with lat/lng)
    - Custom weather conditions (conditions_override)

    Priority:
    - If conditions_override provided, uses custom conditions
    - If location provided (and no override), fetches real weather
    """
    # Shot parameters (flat, not nested)
    ball_speed: float = Field(
        ..., gt=0, le=220,
        description="Ball speed in mph"
    )
    launch_angle: float = Field(
        ..., ge=-10, le=60,
        description="Launch angle in degrees"
    )
    spin_rate: float = Field(
        ..., ge=0, le=15000,
        description="Total spin rate in RPM"
    )
    spin_axis: float = Field(
        default=0, ge=-90, le=90,
        description="Spin axis tilt in degrees (negative = draw, positive = fade)"
    )
    direction: float = Field(
        default=0, ge=-45, le=45,
        description="Initial direction relative to target line"
    )

    # Weather source (one required)
    location: Optional[CoordinateLocation] = Field(
        default=None,
        description="GPS coordinates for weather lookup"
    )
    conditions_override: Optional[ConditionsOverride] = Field(
        default=None,
        description="Custom weather conditions (takes precedence over location)"
    )

    @model_validator(mode='after')
    def validate_weather_source(self):
        """Ensure at least one weather source is provided."""
        if not self.conditions_override and not self.location:
            raise ValueError(
                "Either location or conditions_override required"
            )
        return self


class TrajectoryRequest(BaseModel):
    shot: ShotData
    conditions: WeatherConditions


class TrajectoryLocationRequest(BaseModel):
    shot: ShotData
    location: LocationQuery


class TrajectoryCourseRequest(BaseModel):
    shot: ShotData
    course: CourseQuery


# ============================================================================
# GAMING ENHANCEMENT MODELS
# Extended ranges and new parameters for entertainment venues
# ============================================================================


class GamingShotData(BaseModel):
    """
    Shot data for gaming - can be direct parameters OR handicap/club lookup.
    If player_handicap and club are provided, ball flight parameters are looked up.
    Otherwise, direct parameters (ball_speed_mph, launch_angle_deg, spin_rate_rpm) must be provided.
    """
    # Option A: Direct ball flight parameters (existing behavior)
    ball_speed_mph: Optional[float] = Field(
        default=None, gt=0, le=220,
        description="Ball speed in mph (required if not using handicap/club)"
    )
    launch_angle_deg: Optional[float] = Field(
        default=None, ge=-10, le=60,
        description="Launch angle in degrees (required if not using handicap/club)"
    )
    spin_rate_rpm: Optional[float] = Field(
        default=None, ge=0, le=15000,
        description="Total spin rate in RPM (required if not using handicap/club)"
    )
    spin_axis_deg: float = Field(
        default=0, ge=-90, le=90,
        description="Spin axis tilt in degrees (negative = draw, positive = fade)"
    )
    direction_deg: float = Field(
        default=0, ge=-45, le=45,
        description="Initial direction relative to target line"
    )

    # Option B: Handicap-based lookup (NEW)
    player_handicap: Optional[int] = Field(
        default=None, ge=0, le=36,
        description="Player handicap (0-36). If provided with club, ball flight params are looked up."
    )
    club: Optional[str] = Field(
        default=None,
        description="Club name: driver, 3_wood, 5_wood, 3_iron-9_iron, pw, gw, sw, lw"
    )

    @model_validator(mode='after')
    def validate_shot_params(self):
        """Ensure either handicap/club OR direct params are provided."""
        has_handicap_club = self.player_handicap is not None and self.club is not None
        has_direct_params = all([
            self.ball_speed_mph is not None,
            self.launch_angle_deg is not None,
            self.spin_rate_rpm is not None
        ])

        if not has_handicap_club and not has_direct_params:
            raise ValueError(
                "Either (player_handicap + club) OR (ball_speed_mph + launch_angle_deg + spin_rate_rpm) required"
            )

        return self


class GamingTrajectoryRequest(BaseModel):
    """
    Gaming-enhanced trajectory request.

    Supports:
    - Handicap-based club distances (player_handicap + club)
    - Direct ball flight parameters (ball_speed, launch_angle, spin)
    - Custom weather conditions (conditions_override)
    - Real weather by location (location)

    Priority:
    - If conditions_override provided, uses custom conditions
    - If location provided (and no override), fetches real weather
    - If player_handicap + club provided, looks up stock distances
    - If ball_speed + launch + spin provided, uses direct params
    """
    shot: GamingShotData

    # Weather source (one required)
    conditions_override: Optional[ConditionsOverride] = Field(
        default=None,
        description="Custom weather conditions (takes precedence over location)"
    )
    location: Optional[LocationQuery] = Field(
        default=None,
        description="Location for real weather lookup (used if no conditions_override)"
    )
    preset: Optional[str] = Field(
        default=None,
        description="Weather preset name (e.g., 'hurricane_hero'). Overrides location but not conditions_override."
    )

    @model_validator(mode='after')
    def validate_weather_source(self):
        """Ensure at least one weather source is provided."""
        if not self.conditions_override and not self.location and not self.preset:
            raise ValueError(
                "Either conditions_override, preset, or location required"
            )
        return self

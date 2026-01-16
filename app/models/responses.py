from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class TrajectoryPoint(BaseModel):
    x: float  # Distance downrange (yards)
    y: float  # Height (yards)
    z: float  # Lateral position (yards, positive = right)


class AdjustedResults(BaseModel):
    carry_yards: float
    total_yards: float
    lateral_drift_yards: float
    apex_height_yards: float
    flight_time_seconds: float
    landing_angle_deg: float


class ImpactBreakdown(BaseModel):
    wind_effect_yards: float
    wind_lateral_yards: float
    temperature_effect_yards: float
    altitude_effect_yards: float
    humidity_effect_yards: float
    total_adjustment_yards: float


class ConditionsUsed(BaseModel):
    location: Optional[str] = None
    wind_speed_mph: float
    wind_direction_deg: float
    temperature_f: float
    altitude_ft: float
    humidity_pct: float
    pressure_inhg: float
    conditions_text: Optional[str] = None
    fetched_at: Optional[datetime] = None


class TrajectoryResponse(BaseModel):
    adjusted: AdjustedResults
    baseline: AdjustedResults
    impact_breakdown: ImpactBreakdown
    equivalent_calm_distance_yards: float
    trajectory_points: List[TrajectoryPoint]
    conditions_used: Optional[ConditionsUsed] = None


class ConditionsResponse(BaseModel):
    location: str
    wind_speed_mph: float
    wind_direction_deg: float
    temperature_f: float
    altitude_ft: float
    humidity_pct: float
    pressure_inhg: float
    conditions_text: str
    fetched_at: datetime


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime

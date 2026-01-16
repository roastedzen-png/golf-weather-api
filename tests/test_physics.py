"""
Tests for the physics engine.
"""

import pytest
import math

from app.services.physics import (
    calculate_air_density,
    calculate_drag_coefficient,
    calculate_lift_coefficient,
    calculate_wind_components,
    calculate_trajectory,
    calculate_impact_breakdown,
    STANDARD_AIR_DENSITY,
)
from app.models.requests import ShotData, WeatherConditions


class TestAirDensity:
    """Tests for air density calculation."""

    def test_standard_conditions(self):
        """Standard conditions should give approximately standard air density."""
        # 59°F, sea level, 50% humidity, 29.92 inHg
        density = calculate_air_density(59, 0, 50, 29.92)
        assert 1.1 < density < 1.3  # Should be close to 1.225

    def test_high_altitude_reduces_density(self):
        """Higher altitude should result in lower air density."""
        sea_level = calculate_air_density(70, 0, 50, 29.92)
        mile_high = calculate_air_density(70, 5280, 50, 29.92)
        assert mile_high < sea_level
        # Denver (~5280 ft) should have ~17% less air density
        assert mile_high < sea_level * 0.9

    def test_high_temperature_reduces_density(self):
        """Higher temperature should result in lower air density."""
        cold = calculate_air_density(32, 0, 50, 29.92)
        hot = calculate_air_density(100, 0, 50, 29.92)
        assert hot < cold

    def test_high_humidity_slightly_reduces_density(self):
        """Higher humidity should slightly reduce air density (humid air is lighter)."""
        dry = calculate_air_density(80, 0, 10, 29.92)
        humid = calculate_air_density(80, 0, 90, 29.92)
        # Effect is small but should be measurable
        assert humid < dry


class TestDragCoefficient:
    """Tests for drag coefficient calculation."""

    def test_reasonable_range(self):
        """Drag coefficient should be in expected range for golf balls."""
        cd = calculate_drag_coefficient(2500, 50)
        assert 0.2 < cd < 0.5

    def test_higher_spin_increases_drag(self):
        """Higher spin rate should increase drag coefficient."""
        low_spin = calculate_drag_coefficient(1500, 50)
        high_spin = calculate_drag_coefficient(4000, 50)
        assert high_spin > low_spin

    def test_zero_speed_returns_baseline(self):
        """Zero speed should return baseline drag coefficient."""
        cd = calculate_drag_coefficient(2500, 0)
        assert cd == 0.25


class TestLiftCoefficient:
    """Tests for lift coefficient calculation."""

    def test_reasonable_range(self):
        """Lift coefficient should be in expected range."""
        cl = calculate_lift_coefficient(2500, 50)
        assert 0.1 < cl < 0.5

    def test_higher_spin_increases_lift(self):
        """Higher spin rate should increase lift coefficient."""
        low_spin = calculate_lift_coefficient(1500, 50)
        high_spin = calculate_lift_coefficient(4000, 50)
        assert high_spin > low_spin

    def test_zero_speed_returns_zero(self):
        """Zero speed should return zero lift."""
        cl = calculate_lift_coefficient(2500, 0)
        assert cl == 0.0


class TestWindComponents:
    """Tests for wind component calculation."""

    def test_pure_headwind(self):
        """0 degrees should be pure headwind."""
        headwind, crosswind = calculate_wind_components(10, 0)
        assert headwind > 0
        assert abs(crosswind) < 0.01

    def test_pure_tailwind(self):
        """180 degrees should be pure tailwind."""
        headwind, crosswind = calculate_wind_components(10, 180)
        assert headwind < 0
        assert abs(crosswind) < 0.01

    def test_left_to_right_crosswind(self):
        """90 degrees should be left-to-right crosswind."""
        headwind, crosswind = calculate_wind_components(10, 90)
        assert abs(headwind) < 0.01
        assert crosswind > 0

    def test_right_to_left_crosswind(self):
        """270 degrees should be right-to-left crosswind."""
        headwind, crosswind = calculate_wind_components(10, 270)
        assert abs(headwind) < 0.01
        assert crosswind < 0

    def test_quartering_wind(self):
        """45 degrees should have both headwind and crosswind components."""
        headwind, crosswind = calculate_wind_components(10, 45)
        assert headwind > 0
        assert crosswind > 0
        # Components should be roughly equal at 45 degrees
        assert abs(headwind - crosswind) < 0.5


class TestTrajectory:
    """Tests for trajectory calculation."""

    def test_basic_trajectory(self):
        """Basic trajectory should produce reasonable results."""
        result = calculate_trajectory(
            ball_speed_mph=130,
            launch_angle_deg=14.5,
            spin_rate_rpm=2800,
            spin_axis_deg=0,
            direction_deg=0,
            air_density=STANDARD_AIR_DENSITY,
            headwind_mps=0,
            crosswind_mps=0,
        )

        # Driver shot should carry 150-200 yards
        assert 100 < result["carry_yards"] < 250
        # Apex should be 20-40 yards high
        assert 15 < result["apex_height_yards"] < 50
        # Flight time should be 4-7 seconds
        assert 3 < result["flight_time_seconds"] < 8
        # Landing angle should be 35-55 degrees
        assert 30 < result["landing_angle_deg"] < 60
        # Should have trajectory points
        assert len(result["trajectory_points"]) > 10

    def test_headwind_reduces_distance(self):
        """Headwind should reduce carry distance."""
        no_wind = calculate_trajectory(
            ball_speed_mph=130,
            launch_angle_deg=14.5,
            spin_rate_rpm=2800,
            spin_axis_deg=0,
            direction_deg=0,
            air_density=STANDARD_AIR_DENSITY,
            headwind_mps=0,
            crosswind_mps=0,
        )
        headwind = calculate_trajectory(
            ball_speed_mph=130,
            launch_angle_deg=14.5,
            spin_rate_rpm=2800,
            spin_axis_deg=0,
            direction_deg=0,
            air_density=STANDARD_AIR_DENSITY,
            headwind_mps=10,  # ~22 mph headwind
            crosswind_mps=0,
        )
        assert headwind["carry_yards"] < no_wind["carry_yards"]

    def test_tailwind_increases_distance(self):
        """Tailwind should increase carry distance."""
        no_wind = calculate_trajectory(
            ball_speed_mph=130,
            launch_angle_deg=14.5,
            spin_rate_rpm=2800,
            spin_axis_deg=0,
            direction_deg=0,
            air_density=STANDARD_AIR_DENSITY,
            headwind_mps=0,
            crosswind_mps=0,
        )
        tailwind = calculate_trajectory(
            ball_speed_mph=130,
            launch_angle_deg=14.5,
            spin_rate_rpm=2800,
            spin_axis_deg=0,
            direction_deg=0,
            air_density=STANDARD_AIR_DENSITY,
            headwind_mps=-10,  # ~22 mph tailwind
            crosswind_mps=0,
        )
        assert tailwind["carry_yards"] > no_wind["carry_yards"]

    def test_crosswind_causes_drift(self):
        """Crosswind should cause lateral drift."""
        no_wind = calculate_trajectory(
            ball_speed_mph=130,
            launch_angle_deg=14.5,
            spin_rate_rpm=2800,
            spin_axis_deg=0,
            direction_deg=0,
            air_density=STANDARD_AIR_DENSITY,
            headwind_mps=0,
            crosswind_mps=0,
        )
        crosswind = calculate_trajectory(
            ball_speed_mph=130,
            launch_angle_deg=14.5,
            spin_rate_rpm=2800,
            spin_axis_deg=0,
            direction_deg=0,
            air_density=STANDARD_AIR_DENSITY,
            headwind_mps=0,
            crosswind_mps=5,  # ~11 mph L-to-R
        )
        # Crosswind from left should push ball right (negative z in our convention)
        assert crosswind["lateral_drift_yards"] < no_wind["lateral_drift_yards"]

    def test_lower_air_density_increases_distance(self):
        """Lower air density (altitude/heat) should increase distance."""
        standard = calculate_trajectory(
            ball_speed_mph=130,
            launch_angle_deg=14.5,
            spin_rate_rpm=2800,
            spin_axis_deg=0,
            direction_deg=0,
            air_density=STANDARD_AIR_DENSITY,
            headwind_mps=0,
            crosswind_mps=0,
        )
        thin_air = calculate_trajectory(
            ball_speed_mph=130,
            launch_angle_deg=14.5,
            spin_rate_rpm=2800,
            spin_axis_deg=0,
            direction_deg=0,
            air_density=STANDARD_AIR_DENSITY * 0.85,  # ~Denver altitude
            headwind_mps=0,
            crosswind_mps=0,
        )
        assert thin_air["carry_yards"] > standard["carry_yards"]

    def test_sidespin_causes_curve(self):
        """Sidespin should cause lateral curve (draw/fade)."""
        no_spin = calculate_trajectory(
            ball_speed_mph=130,
            launch_angle_deg=14.5,
            spin_rate_rpm=2800,
            spin_axis_deg=0,  # Pure backspin
            direction_deg=0,
            air_density=STANDARD_AIR_DENSITY,
            headwind_mps=0,
            crosswind_mps=0,
        )
        draw = calculate_trajectory(
            ball_speed_mph=130,
            launch_angle_deg=14.5,
            spin_rate_rpm=2800,
            spin_axis_deg=-15,  # Draw spin
            direction_deg=0,
            air_density=STANDARD_AIR_DENSITY,
            headwind_mps=0,
            crosswind_mps=0,
        )
        fade = calculate_trajectory(
            ball_speed_mph=130,
            launch_angle_deg=14.5,
            spin_rate_rpm=2800,
            spin_axis_deg=15,  # Fade spin
            direction_deg=0,
            air_density=STANDARD_AIR_DENSITY,
            headwind_mps=0,
            crosswind_mps=0,
        )
        # Draw should curve left (negative), fade should curve right (positive)
        assert draw["lateral_drift_yards"] < no_spin["lateral_drift_yards"]
        assert fade["lateral_drift_yards"] > no_spin["lateral_drift_yards"]


class TestImpactBreakdown:
    """Tests for impact breakdown calculation."""

    def test_calm_conditions_no_adjustment(self):
        """Calm, standard conditions should have minimal adjustment."""
        shot = ShotData(
            ball_speed_mph=130,
            launch_angle_deg=14.5,
            spin_rate_rpm=2800,
            spin_axis_deg=0,
            direction_deg=0,
        )
        conditions = WeatherConditions(
            wind_speed_mph=0,
            wind_direction_deg=0,
            temperature_f=59,  # Standard temp
            altitude_ft=0,
            humidity_pct=50,
            pressure_inhg=29.92,
        )
        result = calculate_impact_breakdown(shot, conditions)

        # Total adjustment should be near zero for standard conditions
        assert abs(result["impact_breakdown"]["total_adjustment_yards"]) < 5

    def test_headwind_negative_effect(self):
        """Headwind should have negative effect on distance."""
        shot = ShotData(
            ball_speed_mph=130,
            launch_angle_deg=14.5,
            spin_rate_rpm=2800,
            spin_axis_deg=0,
            direction_deg=0,
        )
        conditions = WeatherConditions(
            wind_speed_mph=20,
            wind_direction_deg=0,  # Headwind
            temperature_f=70,
            altitude_ft=0,
            humidity_pct=50,
            pressure_inhg=29.92,
        )
        result = calculate_impact_breakdown(shot, conditions)

        assert result["impact_breakdown"]["wind_effect_yards"] < 0

    def test_altitude_positive_effect(self):
        """Higher altitude should have positive effect on distance."""
        shot = ShotData(
            ball_speed_mph=130,
            launch_angle_deg=14.5,
            spin_rate_rpm=2800,
            spin_axis_deg=0,
            direction_deg=0,
        )
        conditions = WeatherConditions(
            wind_speed_mph=0,
            wind_direction_deg=0,
            temperature_f=70,
            altitude_ft=5280,  # Denver altitude
            humidity_pct=50,
            pressure_inhg=29.92,
        )
        result = calculate_impact_breakdown(shot, conditions)

        assert result["impact_breakdown"]["altitude_effect_yards"] > 0

    def test_hot_temperature_positive_effect(self):
        """Higher temperature should have positive effect (thinner air)."""
        shot = ShotData(
            ball_speed_mph=130,
            launch_angle_deg=14.5,
            spin_rate_rpm=2800,
            spin_axis_deg=0,
            direction_deg=0,
        )
        conditions = WeatherConditions(
            wind_speed_mph=0,
            wind_direction_deg=0,
            temperature_f=100,  # Hot day
            altitude_ft=0,
            humidity_pct=50,
            pressure_inhg=29.92,
        )
        result = calculate_impact_breakdown(shot, conditions)

        assert result["impact_breakdown"]["temperature_effect_yards"] > 0

    def test_cold_temperature_negative_effect(self):
        """Lower temperature should have negative effect (denser air)."""
        shot = ShotData(
            ball_speed_mph=130,
            launch_angle_deg=14.5,
            spin_rate_rpm=2800,
            spin_axis_deg=0,
            direction_deg=0,
        )
        conditions = WeatherConditions(
            wind_speed_mph=0,
            wind_direction_deg=0,
            temperature_f=40,  # Cold day
            altitude_ft=0,
            humidity_pct=50,
            pressure_inhg=29.92,
        )
        result = calculate_impact_breakdown(shot, conditions)

        assert result["impact_breakdown"]["temperature_effect_yards"] < 0

    def test_baseline_preserved(self):
        """Baseline should be independent of conditions."""
        shot = ShotData(
            ball_speed_mph=130,
            launch_angle_deg=14.5,
            spin_rate_rpm=2800,
            spin_axis_deg=0,
            direction_deg=0,
        )
        conditions1 = WeatherConditions(
            wind_speed_mph=0, altitude_ft=0, temperature_f=70
        )
        conditions2 = WeatherConditions(
            wind_speed_mph=20, altitude_ft=5000, temperature_f=100
        )

        result1 = calculate_impact_breakdown(shot, conditions1)
        result2 = calculate_impact_breakdown(shot, conditions2)

        # Baseline should be the same regardless of conditions
        assert result1["baseline"]["carry_yards"] == result2["baseline"]["carry_yards"]

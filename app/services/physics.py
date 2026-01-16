"""
Golf Ball Physics Engine

Calculates golf ball trajectory accounting for:
- Air density (temperature, altitude, humidity, pressure)
- Wind effects (headwind/tailwind and crosswind)
- Drag and lift forces
- Magnus effect from spin
"""

import math
from typing import Dict, List, Tuple

from app.models.requests import ShotData, WeatherConditions


# Golf ball constants
BALL_MASS_KG = 0.04593  # 1.62 oz
BALL_DIAMETER_M = 0.04267  # 1.68 inches
BALL_RADIUS_M = BALL_DIAMETER_M / 2
BALL_AREA_M2 = math.pi * BALL_RADIUS_M**2

# Standard conditions for baseline
STANDARD_AIR_DENSITY = 1.225  # kg/m³ at sea level, 59°F (15°C)

# Conversion factors
MPH_TO_MPS = 0.44704
FEET_TO_METERS = 0.3048
METERS_TO_YARDS = 1.09361

# Gravity
GRAVITY = 9.81  # m/s²


def calculate_air_density(
    temperature_f: float,
    altitude_ft: float,
    humidity_pct: float,
    pressure_inhg: float,
) -> float:
    """
    Calculate air density in kg/m³.

    Uses the ideal gas law with corrections for humidity and altitude.
    Standard air density at sea level, 59°F, 0% humidity: 1.225 kg/m³

    Args:
        temperature_f: Temperature in Fahrenheit
        altitude_ft: Altitude in feet
        humidity_pct: Relative humidity percentage (0-100)
        pressure_inhg: Barometric pressure in inches of mercury

    Returns:
        Air density in kg/m³
    """
    # Convert units
    temp_c = (temperature_f - 32) * 5 / 9
    temp_k = temp_c + 273.15
    altitude_m = altitude_ft * FEET_TO_METERS
    pressure_pa = pressure_inhg * 3386.39

    # Saturation vapor pressure (Magnus formula) in Pa
    e_s = 6.1078 * (10 ** ((7.5 * temp_c) / (temp_c + 237.3))) * 100

    # Actual vapor pressure
    e = (humidity_pct / 100) * e_s

    # Dry air pressure
    p_d = pressure_pa - e

    # Gas constants
    R_d = 287.05  # Specific gas constant for dry air (J/(kg·K))
    R_v = 461.495  # Specific gas constant for water vapor (J/(kg·K))

    # Air density from ideal gas law
    rho = (p_d / (R_d * temp_k)) + (e / (R_v * temp_k))

    # Altitude adjustment (barometric formula approximation)
    # Scale height of atmosphere is approximately 8500m
    rho = rho * math.exp(-altitude_m / 8500)

    return rho


def calculate_drag_coefficient(spin_rate_rpm: float, ball_speed_mps: float) -> float:
    """
    Calculate drag coefficient based on spin rate and speed.

    Drag coefficient varies with spin rate due to turbulent boundary layer effects.
    Typical range for golf balls: 0.25 - 0.35

    Args:
        spin_rate_rpm: Spin rate in revolutions per minute
        ball_speed_mps: Ball speed in meters per second

    Returns:
        Drag coefficient (dimensionless)
    """
    if ball_speed_mps <= 0:
        return 0.25

    # Spin parameter (ratio of surface speed to ball speed)
    spin_rps = spin_rate_rpm / 60
    spin_parameter = (spin_rps * BALL_RADIUS_M * 2 * math.pi) / ball_speed_mps

    # Base drag coefficient with spin adjustment (empirical fit)
    cd = 0.25 + 0.1 * spin_parameter

    return min(cd, 0.5)  # Cap at reasonable value


def calculate_lift_coefficient(spin_rate_rpm: float, ball_speed_mps: float) -> float:
    """
    Calculate lift coefficient from Magnus effect.

    The Magnus effect creates lift perpendicular to both the velocity and spin axis.
    Backspin creates upward lift, sidespin creates lateral force.

    Args:
        spin_rate_rpm: Spin rate in revolutions per minute
        ball_speed_mps: Ball speed in meters per second

    Returns:
        Lift coefficient (dimensionless)
    """
    if ball_speed_mps <= 0:
        return 0.0

    spin_rps = spin_rate_rpm / 60
    spin_parameter = (spin_rps * BALL_RADIUS_M * 2 * math.pi) / ball_speed_mps

    # Empirical lift coefficient
    cl = 0.15 + 0.2 * spin_parameter

    return min(cl, 0.4)


def calculate_wind_components(
    wind_speed_mph: float, wind_direction_deg: float
) -> Tuple[float, float]:
    """
    Break wind into headwind/tailwind and crosswind components.

    Wind direction convention:
    - 0° = pure headwind (into the golfer's face, ball flying into wind)
    - 90° = left-to-right crosswind
    - 180° = pure tailwind (wind at golfer's back)
    - 270° = right-to-left crosswind

    Args:
        wind_speed_mph: Wind speed in mph
        wind_direction_deg: Wind direction in degrees

    Returns:
        Tuple of (headwind_mps, crosswind_mps)
        - headwind: positive = headwind, negative = tailwind
        - crosswind: positive = left-to-right
    """
    wind_speed_mps = wind_speed_mph * MPH_TO_MPS
    wind_rad = math.radians(wind_direction_deg)

    # Headwind component (positive = headwind, negative = tailwind)
    headwind = wind_speed_mps * math.cos(wind_rad)

    # Crosswind component (positive = left-to-right)
    crosswind = wind_speed_mps * math.sin(wind_rad)

    return headwind, crosswind


def calculate_trajectory(
    ball_speed_mph: float,
    launch_angle_deg: float,
    spin_rate_rpm: float,
    spin_axis_deg: float,
    direction_deg: float,
    air_density: float,
    headwind_mps: float,
    crosswind_mps: float,
    dt: float = 0.01,  # Time step in seconds
) -> Dict:
    """
    Calculate full trajectory using numerical integration (Euler method).

    Args:
        ball_speed_mph: Initial ball speed in mph
        launch_angle_deg: Launch angle in degrees above horizontal
        spin_rate_rpm: Total spin rate in RPM
        spin_axis_deg: Spin axis tilt (-90 to 90, negative = draw spin)
        direction_deg: Initial direction relative to target line
        air_density: Air density in kg/m³
        headwind_mps: Headwind component in m/s (positive = into wind)
        crosswind_mps: Crosswind component in m/s (positive = left-to-right)
        dt: Time step for integration

    Returns:
        Dictionary with trajectory results:
        - carry_yards: Carry distance
        - total_yards: Total distance including roll
        - lateral_drift_yards: Lateral movement (positive = right)
        - apex_height_yards: Maximum height
        - flight_time_seconds: Time in air
        - landing_angle_deg: Descent angle at landing
        - trajectory_points: List of {x, y, z} points
    """
    # Convert inputs to SI units
    ball_speed_mps = ball_speed_mph * MPH_TO_MPS
    launch_rad = math.radians(launch_angle_deg)
    direction_rad = math.radians(direction_deg)
    spin_axis_rad = math.radians(spin_axis_deg)

    # Initial velocity components (x = downrange, y = up, z = lateral)
    vx = ball_speed_mps * math.cos(launch_rad) * math.cos(direction_rad)
    vy = ball_speed_mps * math.sin(launch_rad)
    vz = ball_speed_mps * math.cos(launch_rad) * math.sin(direction_rad)

    # Initial position
    x, y, z = 0.0, 0.0, 0.0

    # Tracking variables
    trajectory_points: List[Dict[str, float]] = [{"x": 0, "y": 0, "z": 0}]
    max_height = 0.0
    flight_time = 0.0
    last_point_time = 0.0

    # Simulation loop - continue until ball hits ground or timeout
    while y >= 0 and flight_time < 15:
        # Velocity relative to air (accounting for wind)
        # Headwind adds to relative velocity in x direction
        # Crosswind subtracts from relative velocity in z direction
        vx_rel = vx + headwind_mps
        vz_rel = vz - crosswind_mps
        v_rel = math.sqrt(vx_rel**2 + vy**2 + vz_rel**2)

        if v_rel < 0.1:
            break

        # Get current coefficients
        cd = calculate_drag_coefficient(spin_rate_rpm, v_rel)
        cl = calculate_lift_coefficient(spin_rate_rpm, v_rel)

        # Drag force factor (0.5 * rho * A * Cd * v)
        drag_factor = 0.5 * air_density * BALL_AREA_M2 * cd * v_rel

        # Drag acceleration components (opposite to relative velocity)
        ax_drag = -drag_factor * vx_rel / BALL_MASS_KG
        ay_drag = -drag_factor * vy / BALL_MASS_KG
        az_drag = -drag_factor * vz_rel / BALL_MASS_KG

        # Lift force factor
        lift_factor = 0.5 * air_density * BALL_AREA_M2 * cl * v_rel

        # Spin axis determines lift direction
        # Pure backspin (axis_deg = 0) creates vertical lift
        # Side spin (axis_deg = ±90) creates lateral force
        backspin_ratio = math.cos(spin_axis_rad)
        sidespin_ratio = math.sin(spin_axis_rad)

        # Lift accelerations
        ay_lift = lift_factor * backspin_ratio / BALL_MASS_KG
        az_lift = lift_factor * sidespin_ratio / BALL_MASS_KG

        # Total acceleration
        ax = ax_drag
        ay = ay_drag + ay_lift - GRAVITY
        az = az_drag + az_lift

        # Update velocity (Euler integration)
        vx += ax * dt
        vy += ay * dt
        vz += az * dt

        # Update position
        x += vx * dt
        y += vy * dt
        z += vz * dt

        # Track maximum height
        if y > max_height:
            max_height = y

        flight_time += dt

        # Store trajectory point every 0.1 seconds
        if flight_time - last_point_time >= 0.1:
            trajectory_points.append(
                {
                    "x": round(x * METERS_TO_YARDS, 1),
                    "y": round(max(0, y) * METERS_TO_YARDS, 1),
                    "z": round(z * METERS_TO_YARDS, 1),
                }
            )
            last_point_time = flight_time

    # Calculate landing angle from final velocity
    landing_speed = math.sqrt(vx**2 + vy**2)
    if landing_speed > 0:
        landing_angle = math.degrees(math.atan2(abs(vy), abs(vx)))
    else:
        landing_angle = 45.0

    # Convert results to yards
    carry_yards = x * METERS_TO_YARDS
    lateral_drift_yards = z * METERS_TO_YARDS
    apex_yards = max_height * METERS_TO_YARDS

    # Estimate roll based on landing angle
    # Steeper landing = less roll, shallower = more roll
    # Typical roll is 5-15% of carry
    roll_factor = max(0.05, 0.15 - (landing_angle - 40) * 0.003)
    roll_yards = carry_yards * roll_factor
    total_yards = carry_yards + roll_yards

    return {
        "carry_yards": round(carry_yards, 1),
        "total_yards": round(total_yards, 1),
        "lateral_drift_yards": round(lateral_drift_yards, 1),
        "apex_height_yards": round(apex_yards, 1),
        "flight_time_seconds": round(flight_time, 2),
        "landing_angle_deg": round(landing_angle, 1),
        "trajectory_points": trajectory_points,
    }


def calculate_impact_breakdown(shot: ShotData, conditions: WeatherConditions) -> Dict:
    """
    Calculate how each weather factor affects distance.

    Compares the adjusted trajectory against a baseline (calm, 70°F, sea level)
    and isolates the effect of each weather variable.

    Args:
        shot: Shot parameters (speed, launch, spin, etc.)
        conditions: Weather conditions

    Returns:
        Dictionary containing:
        - baseline: Trajectory results in standard conditions
        - adjusted: Trajectory results in actual conditions
        - impact_breakdown: Individual effects of each weather factor
        - equivalent_calm_distance_yards: What the shot would go in calm conditions
    """
    # Calculate baseline trajectory (standard conditions, no wind)
    baseline_result = calculate_trajectory(
        ball_speed_mph=shot.ball_speed_mph,
        launch_angle_deg=shot.launch_angle_deg,
        spin_rate_rpm=shot.spin_rate_rpm,
        spin_axis_deg=shot.spin_axis_deg,
        direction_deg=shot.direction_deg,
        air_density=STANDARD_AIR_DENSITY,
        headwind_mps=0,
        crosswind_mps=0,
    )

    # Calculate actual conditions
    actual_density = calculate_air_density(
        conditions.temperature_f,
        conditions.altitude_ft,
        conditions.humidity_pct,
        conditions.pressure_inhg,
    )
    headwind, crosswind = calculate_wind_components(
        conditions.wind_speed_mph, conditions.wind_direction_deg
    )

    # Full adjusted trajectory
    adjusted_result = calculate_trajectory(
        ball_speed_mph=shot.ball_speed_mph,
        launch_angle_deg=shot.launch_angle_deg,
        spin_rate_rpm=shot.spin_rate_rpm,
        spin_axis_deg=shot.spin_axis_deg,
        direction_deg=shot.direction_deg,
        air_density=actual_density,
        headwind_mps=headwind,
        crosswind_mps=crosswind,
    )

    # Isolate wind effect only
    wind_result = calculate_trajectory(
        ball_speed_mph=shot.ball_speed_mph,
        launch_angle_deg=shot.launch_angle_deg,
        spin_rate_rpm=shot.spin_rate_rpm,
        spin_axis_deg=shot.spin_axis_deg,
        direction_deg=shot.direction_deg,
        air_density=STANDARD_AIR_DENSITY,
        headwind_mps=headwind,
        crosswind_mps=crosswind,
    )
    wind_effect = wind_result["carry_yards"] - baseline_result["carry_yards"]
    wind_lateral = wind_result["lateral_drift_yards"] - baseline_result["lateral_drift_yards"]

    # Isolate temperature effect only
    temp_density = calculate_air_density(conditions.temperature_f, 0, 50, 29.92)
    temp_result = calculate_trajectory(
        ball_speed_mph=shot.ball_speed_mph,
        launch_angle_deg=shot.launch_angle_deg,
        spin_rate_rpm=shot.spin_rate_rpm,
        spin_axis_deg=shot.spin_axis_deg,
        direction_deg=shot.direction_deg,
        air_density=temp_density,
        headwind_mps=0,
        crosswind_mps=0,
    )
    temp_effect = temp_result["carry_yards"] - baseline_result["carry_yards"]

    # Isolate altitude effect only
    alt_density = calculate_air_density(70, conditions.altitude_ft, 50, 29.92)
    alt_result = calculate_trajectory(
        ball_speed_mph=shot.ball_speed_mph,
        launch_angle_deg=shot.launch_angle_deg,
        spin_rate_rpm=shot.spin_rate_rpm,
        spin_axis_deg=shot.spin_axis_deg,
        direction_deg=shot.direction_deg,
        air_density=alt_density,
        headwind_mps=0,
        crosswind_mps=0,
    )
    alt_effect = alt_result["carry_yards"] - baseline_result["carry_yards"]

    # Isolate humidity effect only (typically minimal)
    humid_density = calculate_air_density(70, 0, conditions.humidity_pct, 29.92)
    humid_result = calculate_trajectory(
        ball_speed_mph=shot.ball_speed_mph,
        launch_angle_deg=shot.launch_angle_deg,
        spin_rate_rpm=shot.spin_rate_rpm,
        spin_axis_deg=shot.spin_axis_deg,
        direction_deg=shot.direction_deg,
        air_density=humid_density,
        headwind_mps=0,
        crosswind_mps=0,
    )
    humid_effect = humid_result["carry_yards"] - baseline_result["carry_yards"]

    # Total adjustment
    total_adjustment = adjusted_result["carry_yards"] - baseline_result["carry_yards"]

    return {
        "baseline": baseline_result,
        "adjusted": adjusted_result,
        "impact_breakdown": {
            "wind_effect_yards": round(wind_effect, 1),
            "wind_lateral_yards": round(wind_lateral, 1),
            "temperature_effect_yards": round(temp_effect, 1),
            "altitude_effect_yards": round(alt_effect, 1),
            "humidity_effect_yards": round(humid_effect, 1),
            "total_adjustment_yards": round(total_adjustment, 1),
        },
        "equivalent_calm_distance_yards": baseline_result["carry_yards"],
    }

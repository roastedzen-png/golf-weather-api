# Golf Weather Physics API — Full Specification

## Overview

A B2B REST API that calculates how weather conditions affect golf ball flight. Clients send shot data and weather conditions, the API returns adjusted trajectory and impact breakdown.

---

## Tech Stack

- **Language:** Python 3.11+
- **Framework:** FastAPI
- **Weather Data:** WeatherAPI.com (free tier: 1M calls/month)
- **Hosting:** Railway
- **Database:** None (stateless MVP)

---

## Project Structure

```
golf-weather-api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── trajectory.py    # Trajectory endpoints
│   │   └── conditions.py    # Weather condition endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── physics.py       # Physics calculations
│   │   └── weather.py       # Weather API integration
│   ├── models/
│   │   ├── __init__.py
│   │   ├── requests.py      # Pydantic request models
│   │   └── responses.py     # Pydantic response models
│   └── config.py            # Environment variables
├── tests/
│   ├── __init__.py
│   ├── test_physics.py
│   └── test_endpoints.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## API Endpoints

### 1. POST /v1/trajectory

Core physics calculation with manually provided conditions.

**Request Body:**
```json
{
  "shot": {
    "ball_speed_mph": 130,
    "launch_angle_deg": 14.5,
    "spin_rate_rpm": 2800,
    "spin_axis_deg": -2.5,
    "direction_deg": 0
  },
  "conditions": {
    "wind_speed_mph": 15,
    "wind_direction_deg": 0,
    "temperature_f": 55,
    "altitude_ft": 500,
    "humidity_pct": 65,
    "pressure_inhg": 29.92
  }
}
```

**Response Body:**
```json
{
  "adjusted": {
    "carry_yards": 148.2,
    "total_yards": 162.5,
    "lateral_drift_yards": 8.3,
    "apex_height_yards": 28.5,
    "flight_time_seconds": 5.8,
    "landing_angle_deg": 45.2
  },
  "baseline": {
    "carry_yards": 156.0,
    "total_yards": 170.0,
    "lateral_drift_yards": 2.1,
    "apex_height_yards": 31.0,
    "flight_time_seconds": 6.1,
    "landing_angle_deg": 48.0
  },
  "impact_breakdown": {
    "wind_effect_yards": -9.5,
    "wind_lateral_yards": 6.2,
    "temperature_effect_yards": -1.8,
    "altitude_effect_yards": 1.5,
    "humidity_effect_yards": 0.0,
    "total_adjustment_yards": -9.8
  },
  "equivalent_calm_distance_yards": 156.0,
  "trajectory_points": [
    {"x": 0, "y": 0, "z": 0},
    {"x": 10, "y": 5.2, "z": 0.3},
    {"x": 20, "y": 11.1, "z": 0.8}
  ]
}
```

---

### 2. POST /v1/trajectory/location

Physics calculation with weather fetched by city.

**Request Body:**
```json
{
  "shot": {
    "ball_speed_mph": 130,
    "launch_angle_deg": 14.5,
    "spin_rate_rpm": 2800,
    "spin_axis_deg": -2.5,
    "direction_deg": 0
  },
  "location": {
    "city": "Phoenix",
    "state": "AZ",
    "country": "US"
  }
}
```

**Response Body:**
Same as `/v1/trajectory` plus:
```json
{
  "conditions_used": {
    "location": "Phoenix, AZ, US",
    "wind_speed_mph": 8,
    "wind_direction_deg": 225,
    "temperature_f": 92,
    "altitude_ft": 1086,
    "humidity_pct": 12,
    "pressure_inhg": 29.85,
    "fetched_at": "2026-01-16T15:30:00Z"
  }
}
```

---

### 3. POST /v1/trajectory/course

Physics calculation with weather fetched by course name.

**Request Body:**
```json
{
  "shot": {
    "ball_speed_mph": 130,
    "launch_angle_deg": 14.5,
    "spin_rate_rpm": 2800,
    "spin_axis_deg": -2.5,
    "direction_deg": 0
  },
  "course": {
    "name": "TPC Scottsdale"
  }
}
```

**Response Body:**
Same as `/v1/trajectory/location`

**Note:** For MVP, maintain a simple dictionary of ~20-50 popular courses with their lat/long. Expand later.

---

### 4. GET /v1/conditions

Utility endpoint to fetch current conditions without calculating trajectory.

**Query Parameters:**
- `city` (required): City name
- `state` (optional): State/region
- `country` (optional): Country code

**Example:** `GET /v1/conditions?city=Phoenix&state=AZ&country=US`

**Response Body:**
```json
{
  "location": "Phoenix, AZ, US",
  "wind_speed_mph": 8,
  "wind_direction_deg": 225,
  "temperature_f": 92,
  "altitude_ft": 1086,
  "humidity_pct": 12,
  "pressure_inhg": 29.85,
  "conditions_text": "Sunny",
  "fetched_at": "2026-01-16T15:30:00Z"
}
```

---

### 5. GET /v1/health

Status check endpoint.

**Response Body:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-01-16T15:30:00Z"
}
```

---

## Pydantic Models

### Request Models (app/models/requests.py)

```python
from pydantic import BaseModel, Field
from typing import Optional

class ShotData(BaseModel):
    ball_speed_mph: float = Field(..., gt=0, le=220, description="Ball speed in mph")
    launch_angle_deg: float = Field(..., ge=-10, le=60, description="Launch angle in degrees")
    spin_rate_rpm: float = Field(..., ge=0, le=15000, description="Total spin rate in RPM")
    spin_axis_deg: float = Field(default=0, ge=-90, le=90, description="Spin axis tilt in degrees (negative = draw, positive = fade)")
    direction_deg: float = Field(default=0, ge=-45, le=45, description="Initial direction relative to target line")

class WeatherConditions(BaseModel):
    wind_speed_mph: float = Field(default=0, ge=0, le=60, description="Wind speed in mph")
    wind_direction_deg: float = Field(default=0, ge=0, lt=360, description="Wind direction in degrees (0=headwind, 90=left-to-right, 180=tailwind, 270=right-to-left)")
    temperature_f: float = Field(default=70, ge=-20, le=120, description="Temperature in Fahrenheit")
    altitude_ft: float = Field(default=0, ge=-500, le=12000, description="Altitude in feet")
    humidity_pct: float = Field(default=50, ge=0, le=100, description="Relative humidity percentage")
    pressure_inhg: float = Field(default=29.92, ge=27, le=32, description="Barometric pressure in inches of mercury")

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
```

### Response Models (app/models/responses.py)

```python
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
```

---

## Physics Engine (app/services/physics.py)

### Core Formulas

#### 1. Air Density Calculation

Air density affects drag and lift. Calculate using:

```python
def calculate_air_density(temperature_f: float, altitude_ft: float, humidity_pct: float, pressure_inhg: float) -> float:
    """
    Calculate air density in kg/m³
    
    Standard air density at sea level, 59°F, 0% humidity: 1.225 kg/m³
    """
    # Convert units
    temp_c = (temperature_f - 32) * 5/9
    temp_k = temp_c + 273.15
    altitude_m = altitude_ft * 0.3048
    pressure_pa = pressure_inhg * 3386.39
    
    # Saturation vapor pressure (Magnus formula)
    e_s = 6.1078 * 10 ** ((7.5 * temp_c) / (temp_c + 237.3)) * 100  # in Pa
    
    # Actual vapor pressure
    e = (humidity_pct / 100) * e_s
    
    # Dry air pressure
    p_d = pressure_pa - e
    
    # Gas constants
    R_d = 287.05  # Specific gas constant for dry air (J/(kg·K))
    R_v = 461.495  # Specific gas constant for water vapor (J/(kg·K))
    
    # Air density
    rho = (p_d / (R_d * temp_k)) + (e / (R_v * temp_k))
    
    # Altitude adjustment (barometric formula approximation)
    rho = rho * math.exp(-altitude_m / 8500)
    
    return rho

# Standard air density for baseline
STANDARD_AIR_DENSITY = 1.225  # kg/m³ at sea level, 59°F
```

#### 2. Drag and Lift Coefficients

```python
# Golf ball constants
BALL_MASS_KG = 0.04593  # 1.62 oz
BALL_DIAMETER_M = 0.04267  # 1.68 inches
BALL_RADIUS_M = BALL_DIAMETER_M / 2
BALL_AREA_M2 = math.pi * BALL_RADIUS_M ** 2

def calculate_drag_coefficient(spin_rate_rpm: float, ball_speed_mps: float) -> float:
    """
    Drag coefficient varies with spin rate and speed.
    Typical range: 0.25 - 0.35 for golf balls
    """
    # Spin parameter
    spin_rps = spin_rate_rpm / 60
    spin_parameter = (spin_rps * BALL_RADIUS_M) / ball_speed_mps if ball_speed_mps > 0 else 0
    
    # Base drag coefficient (empirical fit)
    cd = 0.25 + 0.1 * spin_parameter
    
    return min(cd, 0.5)  # Cap at reasonable value

def calculate_lift_coefficient(spin_rate_rpm: float, ball_speed_mps: float) -> float:
    """
    Lift coefficient from Magnus effect.
    """
    spin_rps = spin_rate_rpm / 60
    spin_parameter = (spin_rps * BALL_RADIUS_M) / ball_speed_mps if ball_speed_mps > 0 else 0
    
    # Empirical lift coefficient
    cl = 0.15 + 0.2 * spin_parameter
    
    return min(cl, 0.4)
```

#### 3. Wind Effect Calculation

```python
def calculate_wind_components(wind_speed_mph: float, wind_direction_deg: float):
    """
    Break wind into headwind/tailwind and crosswind components.
    
    Wind direction convention:
    - 0° = pure headwind (into the golfer's face)
    - 90° = left-to-right crosswind
    - 180° = pure tailwind
    - 270° = right-to-left crosswind
    """
    wind_speed_mps = wind_speed_mph * 0.44704
    wind_rad = math.radians(wind_direction_deg)
    
    # Headwind component (positive = headwind, negative = tailwind)
    headwind = wind_speed_mps * math.cos(wind_rad)
    
    # Crosswind component (positive = left-to-right)
    crosswind = wind_speed_mps * math.sin(wind_rad)
    
    return headwind, crosswind
```

#### 4. Trajectory Calculation (Simplified 3D)

```python
def calculate_trajectory(
    ball_speed_mph: float,
    launch_angle_deg: float,
    spin_rate_rpm: float,
    spin_axis_deg: float,
    direction_deg: float,
    air_density: float,
    headwind_mps: float,
    crosswind_mps: float,
    dt: float = 0.01  # Time step in seconds
) -> dict:
    """
    Calculate full trajectory using numerical integration.
    Returns carry, total, apex, flight time, landing angle, and trajectory points.
    """
    # Convert inputs
    ball_speed_mps = ball_speed_mph * 0.44704
    launch_rad = math.radians(launch_angle_deg)
    direction_rad = math.radians(direction_deg)
    spin_axis_rad = math.radians(spin_axis_deg)
    
    # Initial velocity components
    vx = ball_speed_mps * math.cos(launch_rad) * math.cos(direction_rad)
    vy = ball_speed_mps * math.sin(launch_rad)
    vz = ball_speed_mps * math.cos(launch_rad) * math.sin(direction_rad)
    
    # Initial position
    x, y, z = 0.0, 0.0, 0.0
    
    # Tracking variables
    trajectory_points = [{"x": 0, "y": 0, "z": 0}]
    max_height = 0.0
    flight_time = 0.0
    
    # Gravity
    g = 9.81
    
    # Simulation loop
    while y >= 0 and flight_time < 15:  # Max 15 seconds
        # Current speed relative to air (accounting for wind)
        vx_rel = vx + headwind_mps
        vz_rel = vz - crosswind_mps
        v_rel = math.sqrt(vx_rel**2 + vy**2 + vz_rel**2)
        
        if v_rel < 0.1:
            break
        
        # Coefficients
        cd = calculate_drag_coefficient(spin_rate_rpm, v_rel)
        cl = calculate_lift_coefficient(spin_rate_rpm, v_rel)
        
        # Drag force magnitude
        drag_factor = 0.5 * air_density * BALL_AREA_M2 * cd * v_rel
        
        # Drag acceleration components
        ax_drag = -drag_factor * vx_rel / BALL_MASS_KG
        ay_drag = -drag_factor * vy / BALL_MASS_KG
        az_drag = -drag_factor * vz_rel / BALL_MASS_KG
        
        # Lift force (Magnus effect)
        lift_factor = 0.5 * air_density * BALL_AREA_M2 * cl * v_rel
        
        # Backspin creates lift (vertical)
        backspin_ratio = math.cos(spin_axis_rad)
        sidespin_ratio = math.sin(spin_axis_rad)
        
        ay_lift = lift_factor * backspin_ratio / BALL_MASS_KG
        az_lift = lift_factor * sidespin_ratio / BALL_MASS_KG
        
        # Total acceleration
        ax = ax_drag
        ay = ay_drag + ay_lift - g
        az = az_drag + az_lift
        
        # Update velocity
        vx += ax * dt
        vy += ay * dt
        vz += az * dt
        
        # Update position
        x += vx * dt
        y += vy * dt
        z += vz * dt
        
        # Track max height
        if y > max_height:
            max_height = y
        
        flight_time += dt
        
        # Store trajectory point every 0.1 seconds
        if int(flight_time * 10) > len(trajectory_points) - 1:
            trajectory_points.append({
                "x": round(x * 1.09361, 1),  # meters to yards
                "y": round(y * 1.09361, 1),
                "z": round(z * 1.09361, 1)
            })
    
    # Calculate landing angle
    landing_speed = math.sqrt(vx**2 + vy**2)
    landing_angle = math.degrees(math.atan2(abs(vy), abs(vx))) if landing_speed > 0 else 45
    
    # Convert to yards
    carry_yards = x * 1.09361
    lateral_drift_yards = z * 1.09361
    apex_yards = max_height * 1.09361
    
    # Estimate roll (simplified: depends on landing angle and conditions)
    # Steeper landing = less roll
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
        "trajectory_points": trajectory_points
    }
```

#### 5. Impact Breakdown Calculation

```python
def calculate_impact_breakdown(
    shot: ShotData,
    conditions: WeatherConditions
) -> dict:
    """
    Calculate how each weather factor affects distance.
    Compare adjusted trajectory vs baseline (calm, 70°F, sea level).
    """
    # Baseline conditions
    baseline_density = STANDARD_AIR_DENSITY
    baseline_result = calculate_trajectory(
        ball_speed_mph=shot.ball_speed_mph,
        launch_angle_deg=shot.launch_angle_deg,
        spin_rate_rpm=shot.spin_rate_rpm,
        spin_axis_deg=shot.spin_axis_deg,
        direction_deg=shot.direction_deg,
        air_density=baseline_density,
        headwind_mps=0,
        crosswind_mps=0
    )
    
    # Actual conditions
    actual_density = calculate_air_density(
        conditions.temperature_f,
        conditions.altitude_ft,
        conditions.humidity_pct,
        conditions.pressure_inhg
    )
    headwind, crosswind = calculate_wind_components(
        conditions.wind_speed_mph,
        conditions.wind_direction_deg
    )
    
    adjusted_result = calculate_trajectory(
        ball_speed_mph=shot.ball_speed_mph,
        launch_angle_deg=shot.launch_angle_deg,
        spin_rate_rpm=shot.spin_rate_rpm,
        spin_axis_deg=shot.spin_axis_deg,
        direction_deg=shot.direction_deg,
        air_density=actual_density,
        headwind_mps=headwind,
        crosswind_mps=crosswind
    )
    
    # Calculate individual effects (isolate each variable)
    
    # Wind only
    wind_result = calculate_trajectory(
        ball_speed_mph=shot.ball_speed_mph,
        launch_angle_deg=shot.launch_angle_deg,
        spin_rate_rpm=shot.spin_rate_rpm,
        spin_axis_deg=shot.spin_axis_deg,
        direction_deg=shot.direction_deg,
        air_density=baseline_density,
        headwind_mps=headwind,
        crosswind_mps=crosswind
    )
    wind_effect = wind_result["carry_yards"] - baseline_result["carry_yards"]
    wind_lateral = wind_result["lateral_drift_yards"] - baseline_result["lateral_drift_yards"]
    
    # Temperature only (affects air density)
    temp_density = calculate_air_density(conditions.temperature_f, 0, 50, 29.92)
    temp_result = calculate_trajectory(
        ball_speed_mph=shot.ball_speed_mph,
        launch_angle_deg=shot.launch_angle_deg,
        spin_rate_rpm=shot.spin_rate_rpm,
        spin_axis_deg=shot.spin_axis_deg,
        direction_deg=shot.direction_deg,
        air_density=temp_density,
        headwind_mps=0,
        crosswind_mps=0
    )
    temp_effect = temp_result["carry_yards"] - baseline_result["carry_yards"]
    
    # Altitude only
    alt_density = calculate_air_density(70, conditions.altitude_ft, 50, 29.92)
    alt_result = calculate_trajectory(
        ball_speed_mph=shot.ball_speed_mph,
        launch_angle_deg=shot.launch_angle_deg,
        spin_rate_rpm=shot.spin_rate_rpm,
        spin_axis_deg=shot.spin_axis_deg,
        direction_deg=shot.direction_deg,
        air_density=alt_density,
        headwind_mps=0,
        crosswind_mps=0
    )
    alt_effect = alt_result["carry_yards"] - baseline_result["carry_yards"]
    
    # Humidity effect (minimal, but calculated)
    humid_density = calculate_air_density(70, 0, conditions.humidity_pct, 29.92)
    humid_result = calculate_trajectory(
        ball_speed_mph=shot.ball_speed_mph,
        launch_angle_deg=shot.launch_angle_deg,
        spin_rate_rpm=shot.spin_rate_rpm,
        spin_axis_deg=shot.spin_axis_deg,
        direction_deg=shot.direction_deg,
        air_density=humid_density,
        headwind_mps=0,
        crosswind_mps=0
    )
    humid_effect = humid_result["carry_yards"] - baseline_result["carry_yards"]
    
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
            "total_adjustment_yards": round(total_adjustment, 1)
        },
        "equivalent_calm_distance_yards": baseline_result["carry_yards"]
    }
```

---

## Weather Service (app/services/weather.py)

```python
import httpx
from datetime import datetime
from app.config import settings

WEATHER_API_BASE = "https://api.weatherapi.com/v1"

async def fetch_weather_by_city(city: str, state: str = None, country: str = "US") -> dict:
    """
    Fetch current weather from WeatherAPI.com
    """
    location = city
    if state:
        location = f"{city},{state}"
    if country:
        location = f"{location},{country}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{WEATHER_API_BASE}/current.json",
            params={
                "key": settings.WEATHER_API_KEY,
                "q": location,
                "aqi": "no"
            }
        )
        response.raise_for_status()
        data = response.json()
    
    current = data["current"]
    location_data = data["location"]
    
    # Get elevation (WeatherAPI doesn't provide this, so we'll need a lookup or default)
    # For MVP, use a simple approximation or hardcoded values for known cities
    altitude_ft = get_city_altitude(city, state, country)
    
    return {
        "location": f"{location_data['name']}, {location_data['region']}, {location_data['country']}",
        "wind_speed_mph": current["wind_mph"],
        "wind_direction_deg": current["wind_degree"],
        "temperature_f": current["temp_f"],
        "altitude_ft": altitude_ft,
        "humidity_pct": current["humidity"],
        "pressure_inhg": current["pressure_in"],
        "conditions_text": current["condition"]["text"],
        "fetched_at": datetime.utcnow()
    }

# Simple altitude lookup for common cities (expand as needed)
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
}

def get_city_altitude(city: str, state: str = None, country: str = "US") -> float:
    """
    Get altitude for a city. Returns 0 (sea level) if unknown.
    """
    key = (city.lower(), state.lower() if state else "", country.lower() if country else "us")
    return CITY_ALTITUDES.get(key, 0)
```

---

## Course Database (app/services/courses.py)

```python
# MVP: Simple dictionary of popular courses
# Expand to database later

COURSES = {
    "tpc scottsdale": {
        "city": "Scottsdale",
        "state": "AZ",
        "country": "US",
        "altitude_ft": 1500
    },
    "pebble beach": {
        "city": "Pebble Beach",
        "state": "CA", 
        "country": "US",
        "altitude_ft": 50
    },
    "st andrews": {
        "city": "St Andrews",
        "state": "Scotland",
        "country": "UK",
        "altitude_ft": 30
    },
    "bandon dunes": {
        "city": "Bandon",
        "state": "OR",
        "country": "US",
        "altitude_ft": 100
    },
    "castle pines": {
        "city": "Castle Rock",
        "state": "CO",
        "country": "US",
        "altitude_ft": 6500
    },
    "pinehurst no 2": {
        "city": "Pinehurst",
        "state": "NC",
        "country": "US",
        "altitude_ft": 525
    },
    "torrey pines": {
        "city": "La Jolla",
        "state": "CA",
        "country": "US",
        "altitude_ft": 340
    },
    "bethpage black": {
        "city": "Farmingdale",
        "state": "NY",
        "country": "US",
        "altitude_ft": 90
    }
}

def get_course_location(course_name: str) -> dict:
    """
    Look up course location by name.
    Returns None if not found.
    """
    key = course_name.lower().strip()
    return COURSES.get(key)
```

---

## Configuration (app/config.py)

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    WEATHER_API_KEY: str
    API_VERSION: str = "1.0.0"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

---

## Environment Variables (.env.example)

```
WEATHER_API_KEY=your_weatherapi_key_here
```

---

## Requirements (requirements.txt)

```
fastapi>=0.109.0
uvicorn>=0.27.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
httpx>=0.26.0
python-dotenv>=1.0.0
pytest>=8.0.0
pytest-asyncio>=0.23.0
```

---

## Main App (app/main.py)

```python
from fastapi import FastAPI
from datetime import datetime
from app.routers import trajectory, conditions
from app.models.responses import HealthResponse
from app.config import settings

app = FastAPI(
    title="Golf Weather Physics API",
    description="Calculate how weather conditions affect golf ball flight",
    version=settings.API_VERSION
)

app.include_router(trajectory.router, prefix="/v1", tags=["Trajectory"])
app.include_router(conditions.router, prefix="/v1", tags=["Conditions"])

@app.get("/v1/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        version=settings.API_VERSION,
        timestamp=datetime.utcnow()
    )
```

---

## Setup Instructions

### 1. Prerequisites

- Python 3.11 or higher
- Git
- A WeatherAPI.com account (free)

### 2. Get WeatherAPI Key

1. Go to https://www.weatherapi.com/
2. Sign up for free account
3. Copy your API key from the dashboard

### 3. Local Development

```bash
# Clone your repo
git clone https://github.com/YOUR_USERNAME/golf-weather-api.git
cd golf-weather-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your WEATHER_API_KEY

# Run the server
uvicorn app.main:app --reload

# API will be available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### 4. Deploy to Railway

1. Go to https://railway.app/
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your golf-weather-api repo
5. Add environment variable: `WEATHER_API_KEY` = your key
6. Railway will auto-detect Python and deploy
7. Get your public URL from the dashboard

---

## Testing

### Sample Curl Commands

```bash
# Health check
curl http://localhost:8000/v1/health

# Basic trajectory (manual conditions)
curl -X POST http://localhost:8000/v1/trajectory \
  -H "Content-Type: application/json" \
  -d '{
    "shot": {
      "ball_speed_mph": 130,
      "launch_angle_deg": 14.5,
      "spin_rate_rpm": 2800,
      "spin_axis_deg": -2,
      "direction_deg": 0
    },
    "conditions": {
      "wind_speed_mph": 15,
      "wind_direction_deg": 0,
      "temperature_f": 55,
      "altitude_ft": 500,
      "humidity_pct": 65
    }
  }'

# Trajectory with location
curl -X POST http://localhost:8000/v1/trajectory/location \
  -H "Content-Type: application/json" \
  -d '{
    "shot": {
      "ball_speed_mph": 130,
      "launch_angle_deg": 14.5,
      "spin_rate_rpm": 2800,
      "spin_axis_deg": -2,
      "direction_deg": 0
    },
    "location": {
      "city": "Phoenix",
      "state": "AZ"
    }
  }'

# Get conditions only
curl "http://localhost:8000/v1/conditions?city=Denver&state=CO"
```

---

## Next Steps After MVP

1. **API Key Authentication** — Add partner API keys and usage tracking
2. **Rate Limiting** — Protect against abuse
3. **Caching** — Cache weather lookups (conditions don't change by the second)
4. **Course Database** — Expand from 8 to 100+ courses
5. **Validation Data** — Partner with a range to compare predictions vs actual
6. **Customer Portal** — Dashboard for partners to see usage

---

## Questions for Claude Code

When you open Claude Code, you can say:

"I have a spec for a Golf Weather Physics API. Here's the document: [paste or reference this file]. Please help me build this step by step, starting with the project structure and core physics engine."

Claude Code will walk you through each file and test as you go.

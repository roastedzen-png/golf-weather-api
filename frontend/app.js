// API Configuration
const API_BASE = 'https://golf-weather-api.vercel.app';

// Calibrated shot parameters that produce accurate carry distances from the physics API
// Each scenario specifies exact ball_speed, launch_angle, spin_rate tuned to produce the target carry
const scenarios = [
    {
        id: 0,
        title: "7-Iron • 165 Yards • Strong Headwind",
        description: "Your standard 7-iron flies 165 yards in calm conditions. But what happens when you're facing a 20 mph headwind at sea level? The ball fights through dense air and loses significant distance.",
        // Calibrated to produce ~165 yard baseline carry
        shot: {
            ball_speed_mph: 160,
            launch_angle_deg: 16,
            spin_rate_rpm: 5500,
            spin_axis_deg: 0,
            direction_deg: 0
        },
        conditions: {
            wind_speed_mph: 20,
            wind_direction_deg: 0,  // Pure headwind
            temperature_f: 70,
            altitude_ft: 0,
            humidity_pct: 50,
            pressure_inhg: 29.92
        },
        standardClub: "7-Iron",
        targetCarry: 165
    },
    {
        id: 1,
        title: "6-Iron • 175 Yards • Denver Summer",
        description: "Playing at 5,280 feet in the Colorado summer. The thin, warm air means your ball will fly much further than the yardage suggests - but how much further?",
        // Calibrated to produce ~175 yard baseline carry
        shot: {
            ball_speed_mph: 172,
            launch_angle_deg: 15,
            spin_rate_rpm: 5000,
            spin_axis_deg: 0,
            direction_deg: 0
        },
        conditions: {
            wind_speed_mph: 5,
            wind_direction_deg: 180,  // Slight tailwind
            temperature_f: 85,
            altitude_ft: 5280,
            humidity_pct: 25,
            pressure_inhg: 29.5
        },
        standardClub: "6-Iron",
        targetCarry: 175
    },
    {
        id: 2,
        title: "8-Iron • 150 Yards • Cold Morning",
        description: "An early morning tee time in 45°F weather. Cold air is dense air, and your ball won't fly as far. Plus the ball itself is colder and less responsive.",
        // Calibrated to produce ~150 yard baseline carry
        shot: {
            ball_speed_mph: 144,
            launch_angle_deg: 17,
            spin_rate_rpm: 6000,
            spin_axis_deg: 0,
            direction_deg: 0
        },
        conditions: {
            wind_speed_mph: 5,
            wind_direction_deg: 0,  // Light headwind
            temperature_f: 45,
            altitude_ft: 500,
            humidity_pct: 70,
            pressure_inhg: 30.1
        },
        standardClub: "8-Iron",
        targetCarry: 150
    },
    {
        id: 3,
        title: "9-Iron • 140 Yards • Crosswind",
        description: "A 15 mph left-to-right crosswind. The ball will drift sideways during flight. How much should you aim left to compensate?",
        // Calibrated to produce ~140 yard baseline carry
        shot: {
            ball_speed_mph: 133,
            launch_angle_deg: 18,
            spin_rate_rpm: 6500,
            spin_axis_deg: 0,
            direction_deg: 0
        },
        conditions: {
            wind_speed_mph: 15,
            wind_direction_deg: 90,  // Left-to-right
            temperature_f: 72,
            altitude_ft: 300,
            humidity_pct: 55,
            pressure_inhg: 29.92
        },
        standardClub: "9-Iron",
        targetCarry: 140
    },
    {
        id: 4,
        title: "Pebble Beach #7 • 107 Yards",
        description: "The famous downhill par 3 overlooking the Pacific Ocean. With a dramatic 50-foot drop from tee to green, the ball stays airborne longer. Coastal winds swirl around this exposed green, making club selection tricky even for the pros.",
        // Calibrated to produce ~107 yard baseline carry (but plays ~90 with elevation)
        shot: {
            ball_speed_mph: 102,
            launch_angle_deg: 22,
            spin_rate_rpm: 8000,
            spin_axis_deg: 0,
            direction_deg: 0
        },
        conditions: {
            wind_speed_mph: 15,
            wind_direction_deg: 45,  // Quartering headwind from left
            temperature_f: 58,
            altitude_ft: 75,
            humidity_pct: 75,
            pressure_inhg: 30.0
        },
        standardClub: "GW",  // 107 yards - 17 yards (50ft drop) = ~90 yards effective
        targetCarry: 107,
        elevation_change_ft: -50  // 50-foot drop from tee to green
    },
    {
        id: 5,
        title: "St Andrews #11 • 172 Yards",
        description: "The Old Course's famous par 3, with its hidden Strath bunker and swirling Scottish winds. The hole plays slightly uphill (~8 feet), requiring extra club in the already challenging Scottish conditions.",
        // Calibrated to produce ~172 yard baseline carry (plays ~175 with elevation)
        shot: {
            ball_speed_mph: 170,
            launch_angle_deg: 15,
            spin_rate_rpm: 5200,
            spin_axis_deg: 0,
            direction_deg: 0
        },
        conditions: {
            wind_speed_mph: 22,
            wind_direction_deg: 315,  // Quartering headwind from right
            temperature_f: 52,
            altitude_ft: 30,
            humidity_pct: 80,
            pressure_inhg: 29.8
        },
        standardClub: "6-Iron",  // 172 yards + 3 yards (8ft climb) = ~175 yards effective
        targetCarry: 172,
        elevation_change_ft: 8  // Slightly uphill
    },
    {
        id: 6,
        title: "TPC Sawgrass #17 • 137 Yards",
        description: "The most famous island green in golf. The hole is essentially flat (no elevation change), but wind swirls unpredictably in the amphitheater setting. There's no bailout - miss the green and you're wet.",
        // Calibrated to produce ~137 yard baseline carry
        shot: {
            ball_speed_mph: 129,
            launch_angle_deg: 19,
            spin_rate_rpm: 6800,
            spin_axis_deg: 0,
            direction_deg: 0
        },
        conditions: {
            wind_speed_mph: 12,
            wind_direction_deg: 225,  // Back-right quartering (helping, pushing left)
            temperature_f: 78,
            altitude_ft: 15,
            humidity_pct: 70,
            pressure_inhg: 29.95
        },
        standardClub: "9-Iron",
        targetCarry: 137,
        elevation_change_ft: 0  // Essentially flat
    }
];

// Mid-handicapper stock distances (carry yards)
// Matched exactly to scenario descriptions:
// - 9-Iron = 140, 8-Iron = 150, 7-Iron = 165, 6-Iron = 175 (from scenarios)
// - ~10-15 yard gaps between clubs
const CLUB_DISTANCES = {
    'LW':     75,
    'SW':     90,
    'GW':     107,   // Pebble Beach #7 is 107 yards
    'PW':     125,
    '9-Iron': 140,   // Scenario 3: 9-Iron = 140 yards
    '8-Iron': 150,   // Scenario 2: 8-Iron = 150 yards
    '7-Iron': 165,   // Scenario 0: 7-Iron = 165 yards
    '6-Iron': 175,   // Scenario 1: 6-Iron = 175 yards
    '5-Iron': 185,
    '4-Iron': 195,
    '5-Wood': 210,
    '3-Wood': 230,
    'Driver': 260
};

// Club data for API calls (ball speed calibrated to produce stock distances)
const CLUB_DATA = {
    'driver':   { ballSpeed: 167, launchAngle: 12, spinRate: 2800, carry: 230, name: 'Driver' },
    '3-wood':   { ballSpeed: 155, launchAngle: 13, spinRate: 3500, carry: 210, name: '3-Wood' },
    '5-wood':   { ballSpeed: 145, launchAngle: 14, spinRate: 4000, carry: 190, name: '5-Wood' },
    '4-iron':   { ballSpeed: 138, launchAngle: 15, spinRate: 4500, carry: 180, name: '4-Iron' },
    '5-iron':   { ballSpeed: 132, launchAngle: 15, spinRate: 5000, carry: 170, name: '5-Iron' },
    '6-iron':   { ballSpeed: 125, launchAngle: 16, spinRate: 5500, carry: 160, name: '6-Iron' },
    '7-iron':   { ballSpeed: 118, launchAngle: 17, spinRate: 6000, carry: 150, name: '7-Iron' },
    '8-iron':   { ballSpeed: 112, launchAngle: 18, spinRate: 6500, carry: 140, name: '8-Iron' },
    '9-iron':   { ballSpeed: 105, launchAngle: 19, spinRate: 7000, carry: 130, name: '9-Iron' },
    'pw':       { ballSpeed: 98,  launchAngle: 21, spinRate: 8000, carry: 120, name: 'PW' },
    'gw':       { ballSpeed: 90,  launchAngle: 24, spinRate: 9000, carry: 105, name: 'GW' },
    'sw':       { ballSpeed: 82,  launchAngle: 28, spinRate: 9500, carry: 90, name: 'SW' },
    'lw':       { ballSpeed: 72,  launchAngle: 32, spinRate: 10000, carry: 75, name: 'LW' }
};

// Get the right club for a given distance
function getClubForDistance(targetYards) {
    const clubs = Object.entries(CLUB_DISTANCES).sort((a, b) => a[1] - b[1]);

    // Find the club closest to the target distance
    let bestClub = clubs[0][0];
    let bestDiff = Math.abs(clubs[0][1] - targetYards);

    for (const [club, dist] of clubs) {
        const diff = Math.abs(dist - targetYards);
        if (diff < bestDiff) {
            bestDiff = diff;
            bestClub = club;
        }
    }

    return bestClub;
}

// Current state
let currentScenario = 0;
let currentWeatherSource = 'manual';  // 'manual', 'location', or 'city'
let fetchedWeatherData = null;        // Stores weather data from API

// Popular US cities for autocomplete (matches backend CITY_ALTITUDES)
const CITY_LIST = [
    { city: 'Phoenix', state: 'AZ', altitude: 1086 },
    { city: 'Denver', state: 'CO', altitude: 5280 },
    { city: 'Scottsdale', state: 'AZ', altitude: 1257 },
    { city: 'Las Vegas', state: 'NV', altitude: 2001 },
    { city: 'Los Angeles', state: 'CA', altitude: 285 },
    { city: 'Miami', state: 'FL', altitude: 6 },
    { city: 'New York', state: 'NY', altitude: 33 },
    { city: 'Chicago', state: 'IL', altitude: 594 },
    { city: 'Atlanta', state: 'GA', altitude: 1050 },
    { city: 'Dallas', state: 'TX', altitude: 430 },
    { city: 'Seattle', state: 'WA', altitude: 175 },
    { city: 'Boston', state: 'MA', altitude: 141 },
    { city: 'San Francisco', state: 'CA', altitude: 52 },
    { city: 'Austin', state: 'TX', altitude: 489 },
    { city: 'Portland', state: 'OR', altitude: 50 },
    { city: 'Salt Lake City', state: 'UT', altitude: 4226 },
    { city: 'Albuquerque', state: 'NM', altitude: 5312 },
    { city: 'Tucson', state: 'AZ', altitude: 2389 },
    { city: 'San Diego', state: 'CA', altitude: 62 },
    { city: 'Orlando', state: 'FL', altitude: 82 },
    { city: 'Houston', state: 'TX', altitude: 80 },
    { city: 'Nashville', state: 'TN', altitude: 597 },
    { city: 'Charlotte', state: 'NC', altitude: 751 },
    { city: 'Minneapolis', state: 'MN', altitude: 830 },
    { city: 'Detroit', state: 'MI', altitude: 600 },
    { city: 'Philadelphia', state: 'PA', altitude: 39 },
    { city: 'Washington', state: 'DC', altitude: 125 },
    { city: 'Tampa', state: 'FL', altitude: 48 },
    { city: 'Raleigh', state: 'NC', altitude: 315 },
    { city: 'Indianapolis', state: 'IN', altitude: 715 },
    { city: 'Wellington', state: 'FL', altitude: 20 },
    { city: 'West Palm Beach', state: 'FL', altitude: 21 },
    { city: 'Fort Lauderdale', state: 'FL', altitude: 9 },
    { city: 'Jacksonville', state: 'FL', altitude: 12 },
    { city: 'Boca Raton', state: 'FL', altitude: 13 },
];

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadScenario(0);
    setupSliderListeners();
    setupCityAutocomplete();
});

// Load a preset scenario
async function loadScenario(index) {
    currentScenario = index;
    const scenario = scenarios[index];

    // Update active state on sidebar
    document.querySelectorAll('.scenario-card').forEach((card, i) => {
        card.classList.toggle('active', i === index);
    });

    // Update header
    document.getElementById('scenario-title').textContent = scenario.title;
    document.getElementById('scenario-description').textContent = scenario.description;

    // Show loading
    showLoading();

    try {
        // Call API with pre-calibrated shot parameters
        const response = await fetch(`${API_BASE}/v1/trajectory`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                shot: scenario.shot,
                conditions: scenario.conditions
            })
        });

        if (!response.ok) throw new Error('API request failed');

        const data = await response.json();
        updateDisplay(data, scenario);
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to calculate trajectory. Please try again.');
    } finally {
        hideLoading();
    }
}

// Update the display with API results
function updateDisplay(data, scenario) {
    const baseline = data.baseline;
    const adjusted = data.adjusted;
    const impact = data.impact_breakdown;
    const conditions = scenario.conditions;
    const elevationFt = scenario.elevation_change_ft || 0;

    // Calculate distances
    const holeDistance = scenario.targetCarry;  // The actual hole distance (e.g., 175 yards)
    const elevationEffect = Math.round(elevationFt / 3);  // ~1 yard per 3 feet (negative = plays shorter)
    const effectiveDistance = holeDistance + elevationEffect;  // What you need to hit

    // Get the club that normally hits this distance (in calm conditions)
    const standardClub = getClubForDistance(effectiveDistance);
    const standardClubDistance = CLUB_DISTANCES[standardClub];

    // Weather effect from API (how much wind/temp/altitude changes carry)
    // Positive = ball flies FURTHER, Negative = ball flies SHORTER
    const weatherEffect = Math.round(adjusted.carry_yards - baseline.carry_yards);

    // What club should you hit to reach the TARGET in these conditions?
    // If weather ADDS distance (weatherEffect > 0), you need a SHORTER club (less distance)
    // If weather SUBTRACTS distance (weatherEffect < 0), you need a LONGER club (more distance)
    //
    // Example: Target = 175 yards, weather adds +6 yards
    // You need a club that normally goes 175 - 6 = 169 yards
    // Because that club + 6 yards of weather boost = 175 yards at the target
    const adjustedNeededDistance = effectiveDistance - weatherEffect;
    const adjustedClub = getClubForDistance(adjustedNeededDistance);
    const adjustedClubDistance = CLUB_DISTANCES[adjustedClub];

    // Standard stats (no weather, with elevation) - what your normal club does in calm
    document.getElementById('std-carry').textContent = effectiveDistance;
    document.getElementById('std-total').textContent = effectiveDistance + 10;  // Approximate roll
    document.getElementById('std-apex').textContent = Math.round(baseline.apex_height_yards);
    document.getElementById('std-drift').textContent = 0;  // No wind = no drift
    document.getElementById('std-flight').textContent = baseline.flight_time_seconds.toFixed(1);
    document.getElementById('std-land').textContent = Math.round(baseline.landing_angle_deg) + '°';
    document.getElementById('std-club').textContent = standardClub;

    // Adjusted stats (with weather)
    // Show what happens if you hit your STANDARD club in these conditions
    // This helps golfers understand: "if I hit my normal club, where will it land?"
    const standardClubWithWeather = standardClubDistance + weatherEffect;
    document.getElementById('adj-carry').textContent = standardClubWithWeather;
    document.getElementById('adj-total').textContent = standardClubWithWeather + 10;
    document.getElementById('adj-apex').textContent = Math.round(adjusted.apex_height_yards);
    document.getElementById('adj-drift').textContent = Math.round(Math.abs(adjusted.lateral_drift_yards));
    document.getElementById('adj-flight').textContent = adjusted.flight_time_seconds.toFixed(1);
    document.getElementById('adj-land').textContent = Math.round(adjusted.landing_angle_deg) + '°';

    // Build recommendation - what club to hit to reach the TARGET
    const driftYards = adjusted.lateral_drift_yards;
    const recommendation = buildRecommendation(standardClub, adjustedClub, weatherEffect, driftYards, elevationFt, holeDistance, effectiveDistance, adjustedClubDistance);
    document.getElementById('adj-club').textContent = recommendation.text;

    // Generate dynamic explanations
    const explanation = generateExplanation(scenario, impact, baseline, adjusted, recommendation);
    document.getElementById('explanation-text').innerHTML = explanation;

    // Generate physics explanation
    const physicsExplanation = generatePhysicsExplanation(scenario, impact);
    document.getElementById('physics-text').innerHTML = physicsExplanation;

    // Deltas (show weather effect - how much further/shorter your standard club goes)
    // This shows the golfer: "Your normal club will fly X yards further/shorter"
    const carryDelta = standardClubWithWeather - effectiveDistance;
    updateDelta('delta-carry', carryDelta);
    updateDelta('delta-total', carryDelta);
    updateDelta('delta-apex', adjusted.apex_height_yards - baseline.apex_height_yards);
    updateDelta('delta-drift', driftYards, true);
    updateDelta('delta-flight', adjusted.flight_time_seconds - baseline.flight_time_seconds);
    updateDelta('delta-land', adjusted.landing_angle_deg - baseline.landing_angle_deg, false, '°');

    // Conditions pills
    document.getElementById('cond-temp').textContent = `🌡️ ${conditions.temperature_f}°F`;
    document.getElementById('cond-wind').textContent = `💨 ${conditions.wind_speed_mph} mph ${getWindDirectionText(conditions.wind_direction_deg)}`;
    document.getElementById('cond-altitude').textContent = conditions.altitude_ft > 100 ? `⛰️ ${conditions.altitude_ft.toLocaleString()} ft` : '⛰️ Sea level';
    document.getElementById('cond-humidity').textContent = `💧 ${conditions.humidity_pct}% humidity`;

    // Elevation change pill (only for scenarios with elevation data)
    const elevationPill = document.getElementById('cond-elevation');
    if (scenario.elevation_change_ft !== undefined && scenario.elevation_change_ft !== 0) {
        const elevFt = scenario.elevation_change_ft;
        const elevText = elevFt < 0
            ? `📐 ${Math.abs(elevFt)} ft drop`
            : `📐 ${elevFt} ft uphill`;
        elevationPill.textContent = elevText;
        elevationPill.style.display = 'inline-block';
    } else {
        elevationPill.style.display = 'none';
    }

    // Impact breakdown
    updateImpactBar('wind', impact.wind_effect_yards);
    updateImpactBar('temp', impact.temperature_effect_yards);
    updateImpactBar('altitude', impact.altitude_effect_yards);
    updateImpactBar('humidity', impact.humidity_effect_yards);

    // Elevation impact (calculated from physics: ~1 yard per 3 feet of elevation change)
    const elevationItem = document.getElementById('elevation-impact-item');
    if (scenario.elevation_change_ft !== undefined && scenario.elevation_change_ft !== 0) {
        // Downhill (negative) = plays shorter = positive yards gained
        // Uphill (positive) = plays longer = negative yards
        const elevImpact = -elevationEffect;  // Flip sign for display (drop = positive benefit)
        updateImpactBar('elevation', elevImpact);
        elevationItem.style.display = 'grid';
    } else {
        elevationItem.style.display = 'none';
    }
}

// Build club recommendation text
// The recommendation answers: "What club should I hit to reach my TARGET distance?"
function buildRecommendation(standardClub, adjustedClub, weatherEffect, driftYards, elevationFt, holeDistance, effectiveDistance, adjustedClubDistance) {
    let text = '';
    let advice = '';

    // Club order from shortest to longest
    const clubOrder = ['LW', 'SW', 'GW', 'PW', '9-Iron', '8-Iron', '7-Iron', '6-Iron', '5-Iron', '4-Iron', '5-Wood', '3-Wood', 'Driver'];
    const stdIdx = clubOrder.indexOf(standardClub);
    const adjIdx = clubOrder.indexOf(adjustedClub);
    const clubDiff = adjIdx - stdIdx;  // Positive = longer club, Negative = shorter club

    if (standardClub === adjustedClub) {
        text = `${adjustedClub} (same club)`;
        advice = `Stick with your ${adjustedClub} - conditions don't significantly change your distance.`;
    } else if (weatherEffect > 0) {
        // Weather ADDS distance (altitude, heat, tailwind)
        // Need a SHORTER club (lower index) to hit the target
        const clubsDown = Math.abs(clubDiff);
        text = `${adjustedClub} (-${clubsDown} club${clubsDown > 1 ? 's' : ''})`;
        advice = `Club DOWN to ${adjustedClub}. The conditions add ~${weatherEffect} yards, so your ${adjustedClub} (normally ${adjustedClubDistance} yds) will carry to the target.`;
    } else {
        // Weather SUBTRACTS distance (cold, headwind)
        // Need a LONGER club (higher index) to hit the target
        const clubsUp = Math.abs(clubDiff);
        text = `${adjustedClub} (+${clubsUp} club${clubsUp > 1 ? 's' : ''})`;
        advice = `Club UP to ${adjustedClub}. The conditions cost you ~${Math.abs(weatherEffect)} yards, so you need more club to reach ${effectiveDistance} yards.`;
    }

    // Add elevation context
    if (elevationFt !== 0) {
        if (elevationFt < 0) {
            advice += ` The ${Math.abs(elevationFt)} ft drop makes this ${holeDistance}-yard hole play like ${effectiveDistance} yards.`;
        } else {
            advice += ` The ${elevationFt} ft climb makes this ${holeDistance}-yard hole play like ${effectiveDistance} yards.`;
        }
    }

    // Add drift advice
    if (Math.abs(driftYards) > 5) {
        const aimDirection = driftYards > 0 ? 'left' : 'right';
        text += `, aim ${Math.abs(Math.round(driftYards))}yds ${aimDirection}`;
        advice += ` Aim ${Math.abs(Math.round(driftYards))} yards ${aimDirection} to compensate for wind drift.`;
    }

    return { text, advice };
}

// Generate physics explanation based on conditions
function generatePhysicsExplanation(scenario, impact) {
    const cond = scenario.conditions;
    const elevationFt = scenario.elevation_change_ft || 0;
    const elevationEffect = Math.abs(elevationFt / 3);  // ~1 yard per 3 feet

    // Determine the dominant factor (include elevation)
    const effects = [
        { name: 'wind', value: Math.abs(impact.wind_effect_yards), raw: impact.wind_effect_yards },
        { name: 'temp', value: Math.abs(impact.temperature_effect_yards), raw: impact.temperature_effect_yards },
        { name: 'altitude', value: Math.abs(impact.altitude_effect_yards), raw: impact.altitude_effect_yards },
        { name: 'humidity', value: Math.abs(impact.humidity_effect_yards), raw: impact.humidity_effect_yards },
        { name: 'elevation', value: elevationEffect, raw: elevationFt }
    ];
    effects.sort((a, b) => b.value - a.value);
    const dominant = effects[0];

    let explanation = '';

    // Wind physics
    if (dominant.name === 'wind' || cond.wind_speed_mph >= 10) {
        const windDir = cond.wind_direction_deg;
        if (windDir < 45 || windDir > 315) {
            // Headwind
            explanation = `<strong>Headwind & Drag:</strong> When the ball flies into a ${cond.wind_speed_mph} mph headwind, its speed <em>relative to the air</em> increases dramatically. Drag force is proportional to velocity squared (F = ½ρv²CdA), so even modest headwinds create significant resistance. <strong>The ball loses energy faster</strong> and drops earlier.`;
        } else if (windDir > 135 && windDir < 225) {
            // Tailwind
            explanation = `<strong>Tailwind & Reduced Drag:</strong> A ${cond.wind_speed_mph} mph tailwind reduces the ball's speed relative to the air. Since drag scales with the square of relative velocity, this significantly decreases air resistance. The ball maintains speed longer and <strong>carries further</strong>, though with a flatter trajectory and more roll.`;
        } else {
            // Crosswind
            const direction = (windDir >= 45 && windDir <= 135) ? 'left-to-right' : 'right-to-left';
            explanation = `<strong>Crosswind & Lateral Force:</strong> The ${cond.wind_speed_mph} mph ${direction} wind exerts a constant sideways force on the ball throughout its flight. This force accumulates over the 5+ seconds of flight time, causing the ball to drift. The effect is <strong>more pronounced for higher shots</strong> that spend more time in the air.`;
        }
    }
    // Altitude physics
    else if (dominant.name === 'altitude' && cond.altitude_ft > 2000) {
        explanation = `<strong>Air Density & Altitude:</strong> At ${cond.altitude_ft.toLocaleString()} feet, air pressure drops significantly (roughly 3% per 1,000 ft). Lower air density means <strong>less drag resistance</strong> on the ball. The same swing produces longer carry because there are fewer air molecules to slow the ball down. Expect 2-3% more distance per 1,000 feet of elevation.`;
    }
    // Temperature physics
    else if (dominant.name === 'temp' || Math.abs(cond.temperature_f - 70) > 15) {
        if (cond.temperature_f < 55) {
            explanation = `<strong>Cold Air Density:</strong> At ${cond.temperature_f}°F, air is denser than at standard temperature (molecules pack closer together). Denser air creates <strong>more drag</strong> on the ball, reducing carry distance. Additionally, cold golf balls compress less at impact, reducing energy transfer. Both effects combine to <strong>shorten your shots</strong>.`;
        } else if (cond.temperature_f > 85) {
            explanation = `<strong>Warm Air Density:</strong> At ${cond.temperature_f}°F, air molecules spread apart, reducing density. Less dense air means <strong>less drag resistance</strong>, so the ball maintains speed longer and carries further. This is why summer rounds often play shorter than the yardage suggests - your ball is genuinely flying further.`;
        } else {
            explanation = `<strong>Standard Conditions:</strong> At ${cond.temperature_f}°F near sea level, air density is close to standard. The primary factor affecting your shot is wind. Air density affects drag force (F = ½ρv²CdA), and at standard conditions, <strong>drag removes about 50% of initial ball energy</strong> by landing.`;
        }
    }
    // Humidity physics (smallest effect)
    else if (dominant.name === 'humidity') {
        explanation = `<strong>Humidity & Air Composition:</strong> Contrary to intuition, humid air is actually <strong>less dense</strong> than dry air. Water molecules (H₂O, mass 18) replace heavier nitrogen (N₂, mass 28) and oxygen (O₂, mass 32) molecules. At ${cond.humidity_pct}% humidity, this slightly reduces air resistance - though the effect is small (typically 1-2 yards).`;
    }
    // Elevation change physics
    else if (dominant.name === 'elevation' && elevationFt !== 0) {
        if (elevationFt < 0) {
            // Downhill
            const playsShorter = Math.abs(elevationFt / 3).toFixed(0);
            explanation = `<strong>Downhill & Projectile Motion:</strong> With a ${Math.abs(elevationFt)}-foot drop from tee to green, gravity works in your favor. The ball's vertical descent is extended because it has further to fall before landing. Using projectile physics, <strong>every 3 feet of drop adds roughly 1 yard to your carry</strong>. This ${Math.abs(elevationFt)}-foot drop means the hole plays approximately <strong>${playsShorter} yards shorter</strong> than the measured distance.`;
        } else {
            // Uphill
            const playsLonger = Math.abs(elevationFt / 3).toFixed(0);
            explanation = `<strong>Uphill & Projectile Motion:</strong> With a ${elevationFt}-foot climb from tee to green, gravity works against you. The ball must rise further before reaching the landing zone, which shortens the horizontal distance traveled. Using projectile physics, <strong>every 3 feet of elevation gain costs roughly 1 yard of carry</strong>. This ${elevationFt}-foot climb means the hole plays approximately <strong>${playsLonger} yards longer</strong> than the measured distance.`;
        }
    }
    // Default explanation
    else {
        explanation = `<strong>Combined Effects:</strong> Multiple weather factors are influencing your shot. Air density (affected by temperature, altitude, and humidity) determines drag force. The drag equation F = ½ρv²CdA shows that <strong>density (ρ) directly scales the resistance</strong> your ball experiences throughout flight.`;
    }

    return explanation;
}

// Generate plain English explanation based on the data
function generateExplanation(scenario, impact, baseline, adjusted, recommendation) {
    const parts = [];
    const carryDiff = adjusted.carry_yards - baseline.carry_yards;
    const driftYards = adjusted.lateral_drift_yards;

    // Wind effect
    if (Math.abs(impact.wind_effect_yards) > 2) {
        if (impact.wind_effect_yards < 0) {
            parts.push(`The wind is costing you <strong>${Math.abs(impact.wind_effect_yards).toFixed(0)} yards</strong> of carry`);
        } else {
            parts.push(`The wind is adding <strong>${impact.wind_effect_yards.toFixed(0)} yards</strong> to your carry`);
        }
    }

    // Temperature effect
    if (Math.abs(impact.temperature_effect_yards) > 1) {
        if (impact.temperature_effect_yards < 0) {
            parts.push(`the cold ${scenario.conditions.temperature_f}°F air adds drag, costing another <strong>${Math.abs(impact.temperature_effect_yards).toFixed(0)} yards</strong>`);
        } else {
            parts.push(`the warm ${scenario.conditions.temperature_f}°F air is thinner, adding <strong>${impact.temperature_effect_yards.toFixed(0)} yards</strong>`);
        }
    }

    // Altitude effect
    if (Math.abs(impact.altitude_effect_yards) > 2) {
        parts.push(`the ${scenario.conditions.altitude_ft.toLocaleString()} ft altitude adds <strong>${impact.altitude_effect_yards.toFixed(0)} yards</strong> due to thinner air`);
    }

    // Combine effects into sentence
    let explanation = '';
    if (parts.length > 0) {
        explanation = parts[0].charAt(0).toUpperCase() + parts[0].slice(1);
        if (parts.length > 1) {
            explanation += ', and ' + parts.slice(1).join(', and ');
        }
        explanation += '. ';
    }

    // Net distance change
    if (Math.abs(carryDiff) > 3) {
        const direction = carryDiff > 0 ? 'further' : 'shorter';
        explanation += `Your ${scenario.standardClub} will fly <strong>${Math.abs(carryDiff).toFixed(0)} yards ${direction}</strong> than normal. `;
    }

    // Drift advice
    if (Math.abs(driftYards) > 3) {
        const driftDirection = driftYards > 0 ? 'right' : 'left';
        explanation += `The ball will drift <strong>${Math.abs(driftYards).toFixed(0)} yards ${driftDirection}</strong> during flight. `;
    }

    // Club recommendation
    explanation += `<strong>${recommendation.advice}</strong>`;

    return explanation;
}

// Helper: Update delta display
function updateDelta(id, value, absolute = false, suffix = '') {
    const el = document.getElementById(id);
    const displayValue = absolute ? value : value;
    const sign = displayValue >= 0 ? '+' : '';
    el.textContent = `${sign}${displayValue.toFixed(1)}${suffix}`;
    el.className = 'stat-delta ' + (displayValue < -0.5 ? 'negative' : displayValue > 0.5 ? 'positive' : '');
}

// Helper: Update impact bar
function updateImpactBar(type, value) {
    const bar = document.getElementById(`bar-${type}`);
    const valueEl = document.getElementById(`impact-${type}`);

    const maxEffect = 20;
    const width = Math.min(Math.abs(value) / maxEffect * 100, 100);

    bar.style.width = `${width}%`;
    bar.className = `impact-bar ${value < 0 ? 'negative' : 'positive'}`;

    const sign = value >= 0 ? '+' : '';
    valueEl.textContent = `${sign}${value.toFixed(1)} yds`;
    valueEl.style.color = value < 0 ? 'var(--negative)' : 'var(--positive)';
}

// Helper: Get wind direction text
function getWindDirectionText(deg) {
    if (deg >= 337.5 || deg < 22.5) return 'headwind';
    if (deg >= 22.5 && deg < 67.5) return 'quartering head-left';
    if (deg >= 67.5 && deg < 112.5) return 'L-to-R crosswind';
    if (deg >= 112.5 && deg < 157.5) return 'quartering tail-left';
    if (deg >= 157.5 && deg < 202.5) return 'tailwind';
    if (deg >= 202.5 && deg < 247.5) return 'quartering tail-right';
    if (deg >= 247.5 && deg < 292.5) return 'R-to-L crosswind';
    if (deg >= 292.5 && deg < 337.5) return 'quartering head-right';
    return '';
}

// Custom panel functions
function showCustomPanel() {
    document.getElementById('custom-panel').classList.add('active');
    document.querySelectorAll('.scenario-card').forEach(card => {
        card.classList.remove('active');
    });
    document.querySelector('.custom-card').classList.add('active');

    // Reset to manual mode when opening the panel
    setWeatherSource('manual');
}

function hideCustomPanel() {
    document.getElementById('custom-panel').classList.remove('active');
}

// Update carry distance when club changes
function updateClubDistance() {
    const select = document.getElementById('club-select');
    const option = select.options[select.selectedIndex];
    const carry = option.getAttribute('data-carry');
    document.getElementById('carry-distance').value = carry;
}

// Setup slider listeners
function setupSliderListeners() {
    const tempSlider = document.getElementById('temperature');
    const tempVal = document.getElementById('temperature-val');
    if (tempSlider) {
        tempSlider.addEventListener('input', () => {
            tempVal.textContent = `${tempSlider.value}°F`;
        });
    }

    const windSlider = document.getElementById('wind-speed');
    const windVal = document.getElementById('wind-speed-val');
    if (windSlider) {
        windSlider.addEventListener('input', () => {
            windVal.textContent = `${windSlider.value} mph`;
        });
    }

    const altSlider = document.getElementById('altitude');
    const altVal = document.getElementById('altitude-val');
    if (altSlider) {
        altSlider.addEventListener('input', () => {
            const alt = parseInt(altSlider.value);
            altVal.textContent = alt === 0 ? 'Sea level' : `${alt.toLocaleString()} ft`;
        });
    }

    const humSlider = document.getElementById('humidity');
    const humVal = document.getElementById('humidity-val');
    if (humSlider) {
        humSlider.addEventListener('input', () => {
            humVal.textContent = `${humSlider.value}%`;
        });
    }
}

// Simulate custom scenario
async function simulateCustom() {
    const clubSelect = document.getElementById('club-select');
    const clubKey = clubSelect.value;
    const club = CLUB_DATA[clubKey];
    const targetCarry = parseInt(document.getElementById('carry-distance').value);

    // Check if we need live weather data but don't have it
    if (currentWeatherSource !== 'manual' && !fetchedWeatherData) {
        alert('Please fetch weather data first by clicking "Get Weather" or "Use My Current Location".');
        return;
    }

    // Scale ball speed to achieve desired carry
    const carryRatio = targetCarry / club.carry;
    const scaledBallSpeed = Math.round(club.ballSpeed * Math.sqrt(carryRatio));

    const shot = {
        ball_speed_mph: scaledBallSpeed,
        launch_angle_deg: club.launchAngle,
        spin_rate_rpm: club.spinRate,
        spin_axis_deg: 0,
        direction_deg: 0
    };

    // Use fetched weather data if available, otherwise use manual slider values
    let conditions;
    let locationName = 'Custom';

    if (currentWeatherSource !== 'manual' && fetchedWeatherData) {
        // Use API data directly for more accuracy
        conditions = {
            wind_speed_mph: fetchedWeatherData.wind_speed_mph,
            wind_direction_deg: fetchedWeatherData.wind_direction_deg,
            temperature_f: fetchedWeatherData.temperature_f,
            altitude_ft: fetchedWeatherData.altitude_ft,
            humidity_pct: fetchedWeatherData.humidity_pct,
            pressure_inhg: fetchedWeatherData.pressure_inhg
        };
        // Extract city name for display
        locationName = fetchedWeatherData.location.split(',')[0];
    } else {
        conditions = {
            wind_speed_mph: parseFloat(document.getElementById('wind-speed').value),
            wind_direction_deg: parseFloat(document.getElementById('wind-direction').value),
            temperature_f: parseFloat(document.getElementById('temperature').value),
            altitude_ft: parseFloat(document.getElementById('altitude').value),
            humidity_pct: parseFloat(document.getElementById('humidity').value),
            pressure_inhg: 29.92
        };
    }

    // Update header
    document.getElementById('scenario-title').textContent = `${club.name} • ${targetCarry} Yards • ${locationName}`;
    const descriptionSuffix = currentWeatherSource !== 'manual' && fetchedWeatherData
        ? `Using live weather from ${fetchedWeatherData.location}. ${fetchedWeatherData.conditions_text}.`
        : 'See how your custom weather conditions affect the shot.';
    document.getElementById('scenario-description').textContent =
        `Your ${club.name} that normally carries ${targetCarry} yards. ${descriptionSuffix}`;

    showLoading();
    hideCustomPanel();

    try {
        const response = await fetch(`${API_BASE}/v1/trajectory`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ shot, conditions })
        });

        if (!response.ok) throw new Error('API request failed');

        const data = await response.json();

        // Create custom scenario for display
        const customScenario = {
            conditions,
            standardClub: club.name,
            targetCarry: targetCarry,
            shot: shot
        };

        updateDisplay(data, customScenario);
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to calculate trajectory. Please try again.');
    } finally {
        hideLoading();
    }
}

// Modal functions
function showPlaceholder(feature) {
    document.getElementById('modal-title').textContent = feature;
    document.getElementById('modal-text').textContent =
        `The ${feature} feature is coming soon. This is a placeholder for future development.`;
    document.getElementById('modal-overlay').classList.add('active');
}

function hideModal() {
    document.getElementById('modal-overlay').classList.remove('active');
}

// Loading functions
function showLoading() {
    document.getElementById('loading').classList.add('active');
}

function hideLoading() {
    document.getElementById('loading').classList.remove('active');
}

// Weather Source Management
function setWeatherSource(source) {
    currentWeatherSource = source;
    fetchedWeatherData = null;  // Reset fetched data when changing source

    // Update toggle button states
    document.querySelectorAll('.source-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.source === source);
    });

    // Show/hide location input section
    const locationSection = document.getElementById('location-input-section');
    const cityGroup = document.getElementById('city-input-group');
    const locationGroup = document.getElementById('current-location-group');
    const weatherControls = document.getElementById('weather-controls');
    const weatherStatus = document.getElementById('weather-status');

    if (source === 'manual') {
        locationSection.style.display = 'none';
        weatherControls.classList.remove('disabled');
        weatherStatus.style.display = 'none';
    } else {
        locationSection.style.display = 'block';
        weatherControls.classList.add('disabled');

        if (source === 'city') {
            cityGroup.style.display = 'block';
            locationGroup.style.display = 'none';
        } else if (source === 'location') {
            cityGroup.style.display = 'none';
            locationGroup.style.display = 'block';
        }
    }
}

// Fetch weather by city name
async function fetchWeatherByCity() {
    const cityInput = document.getElementById('city-input');
    const city = cityInput.value.trim();

    if (!city) {
        showWeatherStatus('error', 'Please enter a city name');
        return;
    }

    showWeatherStatus('loading', 'Fetching weather data...');

    try {
        const response = await fetch(`${API_BASE}/v1/conditions?city=${encodeURIComponent(city)}`);

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to fetch weather');
        }

        const data = await response.json();
        fetchedWeatherData = data;
        updateWeatherControlsFromAPI(data);
        showWeatherStatus('success', `Weather loaded for <span class="location-name">${data.location}</span><br>${data.conditions_text}, ${Math.round(data.temperature_f)}°F`);

    } catch (error) {
        console.error('Weather fetch error:', error);
        showWeatherStatus('error', `Could not fetch weather: ${error.message}`);
        fetchedWeatherData = null;
    }
}

// Fetch weather by current location (geolocation)
async function fetchWeatherByCurrentLocation() {
    if (!navigator.geolocation) {
        showWeatherStatus('error', 'Geolocation is not supported by your browser');
        return;
    }

    showWeatherStatus('loading', 'Getting your location...');

    navigator.geolocation.getCurrentPosition(
        async (position) => {
            const { latitude, longitude, accuracy } = position.coords;

            // Log coordinates for debugging
            console.log(`Geolocation: lat=${latitude}, lon=${longitude}, accuracy=${accuracy}m`);
            showWeatherStatus('loading', `Found location (${latitude.toFixed(4)}, ${longitude.toFixed(4)}). Fetching weather...`);

            try {
                // Try the dedicated coordinates endpoint first, fall back to city endpoint with lat,lon
                let response = await fetch(`${API_BASE}/v1/conditions/coords?lat=${latitude}&lon=${longitude}`);

                // If coords endpoint doesn't exist (404), fall back to using lat,lon as city query
                if (response.status === 404) {
                    response = await fetch(`${API_BASE}/v1/conditions?city=${latitude},${longitude}`);
                }

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Failed to fetch weather');
                }

                const data = await response.json();
                fetchedWeatherData = data;
                updateWeatherControlsFromAPI(data);
                showWeatherStatus('success', `Weather loaded for <span class="location-name">${data.location}</span><br>${data.conditions_text}, ${Math.round(data.temperature_f)}°F`);

            } catch (error) {
                console.error('Weather fetch error:', error);
                showWeatherStatus('error', `Could not fetch weather: ${error.message}`);
                fetchedWeatherData = null;
            }
        },
        (error) => {
            let message = 'Could not get your location';
            switch (error.code) {
                case error.PERMISSION_DENIED:
                    message = 'Location access was denied. Please enable location permissions.';
                    break;
                case error.POSITION_UNAVAILABLE:
                    message = 'Location information is unavailable.';
                    break;
                case error.TIMEOUT:
                    message = 'Location request timed out.';
                    break;
            }
            showWeatherStatus('error', message);
            fetchedWeatherData = null;
        },
        {
            enableHighAccuracy: true,  // Request high accuracy for better location
            timeout: 10000,
            maximumAge: 60000  // Cache location for 1 minute
        }
    );
}

// Update the weather controls to show fetched values (visual feedback)
function updateWeatherControlsFromAPI(data) {
    // Update slider values to match API data
    const tempSlider = document.getElementById('temperature');
    const windSlider = document.getElementById('wind-speed');
    const altSlider = document.getElementById('altitude');
    const humSlider = document.getElementById('humidity');
    const windDirSelect = document.getElementById('wind-direction');

    // Set temperature (clamp to slider range)
    const temp = Math.max(30, Math.min(110, Math.round(data.temperature_f)));
    tempSlider.value = temp;
    document.getElementById('temperature-val').textContent = `${temp}°F`;

    // Set wind speed (clamp to slider range)
    const wind = Math.max(0, Math.min(35, Math.round(data.wind_speed_mph)));
    windSlider.value = wind;
    document.getElementById('wind-speed-val').textContent = `${wind} mph`;

    // Set altitude (clamp to slider range)
    const alt = Math.max(0, Math.min(7000, Math.round(data.altitude_ft)));
    altSlider.value = alt;
    document.getElementById('altitude-val').textContent = alt === 0 ? 'Sea level' : `${alt.toLocaleString()} ft`;

    // Set humidity (clamp to slider range)
    const hum = Math.max(10, Math.min(100, Math.round(data.humidity_pct)));
    humSlider.value = hum;
    document.getElementById('humidity-val').textContent = `${hum}%`;

    // Set wind direction to nearest option
    const windDir = data.wind_direction_deg;
    const options = [0, 45, 90, 135, 180, 225, 270, 315];
    const closest = options.reduce((prev, curr) =>
        Math.abs(curr - windDir) < Math.abs(prev - windDir) ? curr : prev
    );
    windDirSelect.value = closest;
}

// Show weather status message
function showWeatherStatus(type, message) {
    const status = document.getElementById('weather-status');
    const icon = document.getElementById('weather-status-icon');
    const text = document.getElementById('weather-status-text');

    status.style.display = 'flex';
    status.className = 'weather-status ' + type;

    switch (type) {
        case 'loading':
            icon.textContent = '⏳';
            break;
        case 'success':
            icon.textContent = '✅';
            break;
        case 'error':
            icon.textContent = '❌';
            break;
    }

    text.innerHTML = message;
}

// City Autocomplete Functions
function setupCityAutocomplete() {
    const input = document.getElementById('city-input');
    const suggestions = document.getElementById('city-suggestions');

    if (!input || !suggestions) return;

    let debounceTimer;

    input.addEventListener('input', (e) => {
        clearTimeout(debounceTimer);
        const query = e.target.value.trim().toLowerCase();

        if (query.length < 2) {
            hideCitySuggestions();
            return;
        }

        debounceTimer = setTimeout(() => {
            showCitySuggestions(query);
        }, 150);
    });

    input.addEventListener('focus', () => {
        const query = input.value.trim().toLowerCase();
        if (query.length >= 2) {
            showCitySuggestions(query);
        }
    });

    // Hide suggestions when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.city-input-container')) {
            hideCitySuggestions();
        }
    });

    // Handle keyboard navigation
    input.addEventListener('keydown', (e) => {
        const items = suggestions.querySelectorAll('.city-suggestion-item');
        const activeItem = suggestions.querySelector('.city-suggestion-item.active');
        let activeIndex = Array.from(items).indexOf(activeItem);

        if (e.key === 'ArrowDown') {
            e.preventDefault();
            if (activeIndex < items.length - 1) {
                items[activeIndex]?.classList.remove('active');
                items[activeIndex + 1]?.classList.add('active');
            } else if (activeIndex === -1 && items.length > 0) {
                items[0]?.classList.add('active');
            }
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            if (activeIndex > 0) {
                items[activeIndex]?.classList.remove('active');
                items[activeIndex - 1]?.classList.add('active');
            }
        } else if (e.key === 'Enter') {
            if (activeItem) {
                e.preventDefault();
                selectCity(activeItem.dataset.city, activeItem.dataset.state);
            }
        } else if (e.key === 'Escape') {
            hideCitySuggestions();
        }
    });
}

function showCitySuggestions(query) {
    const suggestions = document.getElementById('city-suggestions');

    // Filter cities that match the query
    const matches = CITY_LIST.filter(item => {
        const cityMatch = item.city.toLowerCase().includes(query);
        const stateMatch = item.state.toLowerCase().includes(query);
        const fullMatch = `${item.city}, ${item.state}`.toLowerCase().includes(query);
        return cityMatch || stateMatch || fullMatch;
    }).slice(0, 6);  // Limit to 6 suggestions

    if (matches.length === 0) {
        hideCitySuggestions();
        return;
    }

    suggestions.innerHTML = matches.map(item => `
        <div class="city-suggestion-item"
             data-city="${item.city}"
             data-state="${item.state}"
             onclick="selectCity('${item.city}', '${item.state}')">
            <div class="city-name">${item.city}, ${item.state}</div>
            <div class="city-details">${item.altitude.toLocaleString()} ft elevation</div>
        </div>
    `).join('');

    suggestions.classList.add('active');
}

function hideCitySuggestions() {
    const suggestions = document.getElementById('city-suggestions');
    if (suggestions) {
        suggestions.classList.remove('active');
    }
}

function selectCity(city, state) {
    const input = document.getElementById('city-input');
    input.value = `${city}, ${state}`;
    hideCitySuggestions();

    // Automatically fetch weather for the selected city
    fetchWeatherByCity();
}

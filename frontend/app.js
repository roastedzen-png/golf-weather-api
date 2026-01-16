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
        title: "Pebble Beach #7 • PW • 107 Yards",
        description: "The famous downhill par 3 overlooking the Pacific Ocean. With a dramatic 50-foot drop from tee to green, the ball stays airborne longer. Coastal winds swirl around this exposed green, making club selection tricky even for the pros.",
        // Calibrated to produce ~107 yard baseline carry
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
        standardClub: "PW",
        targetCarry: 107,
        elevation_change_ft: -50  // 50-foot drop from tee to green
    },
    {
        id: 5,
        title: "St Andrews #11 • 7-Iron • 172 Yards",
        description: "The Old Course's famous par 3, with its hidden Strath bunker and swirling Scottish winds. The hole plays slightly uphill (~8 feet), requiring extra club in the already challenging Scottish conditions.",
        // Calibrated to produce ~172 yard baseline carry
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
        standardClub: "7-Iron",
        targetCarry: 172,
        elevation_change_ft: 8  // Slightly uphill
    },
    {
        id: 6,
        title: "TPC Sawgrass #17 • 9-Iron • 137 Yards",
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

// Club data for custom scenario builder
const CLUB_DATA = {
    'driver':   { ballSpeed: 180, launchAngle: 12, spinRate: 2800, carry: 190, name: 'Driver' },
    '3-wood':   { ballSpeed: 172, launchAngle: 13, spinRate: 3500, carry: 180, name: '3-Wood' },
    '5-wood':   { ballSpeed: 165, launchAngle: 14, spinRate: 4000, carry: 170, name: '5-Wood' },
    '4-iron':   { ballSpeed: 160, launchAngle: 15, spinRate: 4500, carry: 165, name: '4-Iron' },
    '5-iron':   { ballSpeed: 155, launchAngle: 15, spinRate: 5000, carry: 160, name: '5-Iron' },
    '6-iron':   { ballSpeed: 150, launchAngle: 16, spinRate: 5500, carry: 150, name: '6-Iron' },
    '7-iron':   { ballSpeed: 145, launchAngle: 17, spinRate: 6000, carry: 145, name: '7-Iron' },
    '8-iron':   { ballSpeed: 138, launchAngle: 18, spinRate: 6500, carry: 135, name: '8-Iron' },
    '9-iron':   { ballSpeed: 130, launchAngle: 19, spinRate: 7000, carry: 125, name: '9-Iron' },
    'pw':       { ballSpeed: 120, launchAngle: 21, spinRate: 8000, carry: 115, name: 'PW' },
    'gw':       { ballSpeed: 110, launchAngle: 24, spinRate: 9000, carry: 100, name: 'GW' },
    'sw':       { ballSpeed: 100, launchAngle: 28, spinRate: 9500, carry: 90, name: 'SW' },
    'lw':       { ballSpeed: 90,  launchAngle: 32, spinRate: 10000, carry: 75, name: 'LW' }
};

// Current state
let currentScenario = 0;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadScenario(0);
    setupSliderListeners();
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

    // Standard stats (baseline - your normal shot in calm conditions)
    document.getElementById('std-carry').textContent = Math.round(baseline.carry_yards);
    document.getElementById('std-total').textContent = Math.round(baseline.total_yards);
    document.getElementById('std-apex').textContent = Math.round(baseline.apex_height_yards);
    document.getElementById('std-drift').textContent = Math.round(Math.abs(baseline.lateral_drift_yards));
    document.getElementById('std-flight').textContent = baseline.flight_time_seconds.toFixed(1);
    document.getElementById('std-land').textContent = Math.round(baseline.landing_angle_deg) + '°';
    document.getElementById('std-club').textContent = scenario.standardClub;

    // Adjusted stats (with weather)
    document.getElementById('adj-carry').textContent = Math.round(adjusted.carry_yards);
    document.getElementById('adj-total').textContent = Math.round(adjusted.total_yards);
    document.getElementById('adj-apex').textContent = Math.round(adjusted.apex_height_yards);
    document.getElementById('adj-drift').textContent = Math.round(Math.abs(adjusted.lateral_drift_yards));
    document.getElementById('adj-flight').textContent = adjusted.flight_time_seconds.toFixed(1);
    document.getElementById('adj-land').textContent = Math.round(adjusted.landing_angle_deg) + '°';

    // Calculate recommended club and generate explanation
    const carryDiff = adjusted.carry_yards - baseline.carry_yards;
    const driftYards = adjusted.lateral_drift_yards;
    const recommendation = getClubRecommendation(scenario.standardClub, carryDiff, driftYards, scenario.targetCarry);
    document.getElementById('adj-club').textContent = recommendation.text;

    // Generate dynamic explanations
    const explanation = generateExplanation(scenario, impact, baseline, adjusted, recommendation);
    document.getElementById('explanation-text').innerHTML = explanation;

    // Generate physics explanation
    const physicsExplanation = generatePhysicsExplanation(scenario, impact);
    document.getElementById('physics-text').innerHTML = physicsExplanation;

    // Deltas
    updateDelta('delta-carry', carryDiff);
    updateDelta('delta-total', adjusted.total_yards - baseline.total_yards);
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
        // Downhill (negative elevation) plays shorter, uphill plays longer
        // Physics: ball in flight longer when dropping, shorter flight when climbing
        const elevationEffect = -scenario.elevation_change_ft / 3;  // ~1 yard per 3 feet
        updateImpactBar('elevation', elevationEffect);
        elevationItem.style.display = 'grid';
    } else {
        elevationItem.style.display = 'none';
    }
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

// Get club recommendation based on distance difference
function getClubRecommendation(originalClub, carryDiff, driftYards, targetCarry) {
    const clubOrder = ['LW', 'SW', 'GW', 'PW', '9-Iron', '8-Iron', '7-Iron', '6-Iron', '5-Iron', '4-Iron', '5-Wood', '3-Wood', 'Driver'];
    const currentIndex = clubOrder.findIndex(c => c.toLowerCase() === originalClub.toLowerCase());

    let text = '';
    let advice = '';
    let clubsChange = 0;

    // Calculate clubs needed based on ~10 yards per club
    if (carryDiff < -15) {
        clubsChange = 2;
    } else if (carryDiff < -7) {
        clubsChange = 1;
    } else if (carryDiff > 15) {
        clubsChange = -2;
    } else if (carryDiff > 7) {
        clubsChange = -1;
    }

    if (clubsChange > 0) {
        const newIndex = Math.min(currentIndex + clubsChange, clubOrder.length - 1);
        const newClub = clubOrder[newIndex];
        text = `${newClub} (+${clubsChange} club${clubsChange > 1 ? 's' : ''})`;
        advice = `Club up to a ${newClub} to reach your ${targetCarry}-yard target.`;
    } else if (clubsChange < 0) {
        const newIndex = Math.max(currentIndex + clubsChange, 0);
        const newClub = clubOrder[newIndex];
        text = `${newClub} (${clubsChange} club${clubsChange < -1 ? 's' : ''})`;
        advice = `Club down to a ${newClub} - the ball will fly further than normal.`;
    } else {
        text = `${originalClub} (same club)`;
        advice = `Stick with your ${originalClub}.`;
    }

    // Add drift advice
    if (Math.abs(driftYards) > 5) {
        const aimDirection = driftYards > 0 ? 'left' : 'right';
        text += `, aim ${Math.abs(Math.round(driftYards))}yds ${aimDirection}`;
        advice += ` Aim ${Math.abs(Math.round(driftYards))} yards ${aimDirection} to compensate for wind drift.`;
    }

    return { text, advice };
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

    const conditions = {
        wind_speed_mph: parseFloat(document.getElementById('wind-speed').value),
        wind_direction_deg: parseFloat(document.getElementById('wind-direction').value),
        temperature_f: parseFloat(document.getElementById('temperature').value),
        altitude_ft: parseFloat(document.getElementById('altitude').value),
        humidity_pct: parseFloat(document.getElementById('humidity').value),
        pressure_inhg: 29.92
    };

    // Update header
    document.getElementById('scenario-title').textContent = `${club.name} • ${targetCarry} Yards • Custom`;
    document.getElementById('scenario-description').textContent =
        `Your ${club.name} that normally carries ${targetCarry} yards. See how your custom weather conditions affect the shot.`;

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

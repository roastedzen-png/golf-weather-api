// API Configuration
const API_BASE = 'https://golf-weather-api.vercel.app';

// Scenario Data
const scenarios = [
    {
        id: 0,
        title: "Pebble Beach #7 - Coastal Wind Challenge",
        description: "A 107-yard downhill par 3 overlooking the Pacific Ocean. January brings cool temperatures and swirling coastal winds that can turn a simple wedge into a guessing game.",
        shot: {
            ball_speed_mph: 95,
            launch_angle_deg: 28,
            spin_rate_rpm: 8500,
            spin_axis_deg: 0,
            direction_deg: 0
        },
        conditions: {
            wind_speed_mph: 15,
            wind_direction_deg: 45,
            temperature_f: 54,
            altitude_ft: 50,
            humidity_pct: 78,
            pressure_inhg: 30.1
        },
        standardClub: "Pitching Wedge",
        adjustedClub: "9-Iron (aim 10yds left)",
        explanation: "The 15 mph ocean wind is the biggest factor here, costing you <strong>significant carry distance</strong>. Combined with the cool 54°F temperature (denser air = more drag), your standard pitching wedge will come up short. <strong>Club up to a 9-iron</strong> and aim left to account for the left-to-right wind drift. The ball will land at a slightly shallower angle, so expect <strong>more roll than usual</strong> on this firm coastal green."
    },
    {
        id: 1,
        title: "Castle Pines #18 - Mile High Finish",
        description: "A demanding 175-yard approach shot at 6,500 feet elevation. The thin Colorado air means your ball will fly further than at sea level - but how much further?",
        shot: {
            ball_speed_mph: 115,
            launch_angle_deg: 18,
            spin_rate_rpm: 6000,
            spin_axis_deg: 0,
            direction_deg: 0
        },
        conditions: {
            wind_speed_mph: 5,
            wind_direction_deg: 180,
            temperature_f: 78,
            altitude_ft: 6500,
            humidity_pct: 25,
            pressure_inhg: 29.5
        },
        standardClub: "6-Iron",
        adjustedClub: "7-Iron (plays 10% shorter)",
        explanation: "At 6,500 feet, the air is <strong>15-20% thinner</strong> than at sea level. This dramatically reduces drag, adding significant distance to every shot. Combined with the warm temperature and slight tailwind, your ball will fly much further than the yardage suggests. <strong>Club down to a 7-iron</strong> - the altitude effect alone adds nearly 15 yards to your carry."
    },
    {
        id: 2,
        title: "TPC Scottsdale #16 - Desert Heat",
        description: "The famous stadium par 3, playing 162 yards in the Arizona summer. When temperatures hit 105°F, the thin, hot air changes everything about club selection.",
        shot: {
            ball_speed_mph: 105,
            launch_angle_deg: 22,
            spin_rate_rpm: 7000,
            spin_axis_deg: 2,
            direction_deg: 0
        },
        conditions: {
            wind_speed_mph: 8,
            wind_direction_deg: 90,
            temperature_f: 105,
            altitude_ft: 1500,
            humidity_pct: 12,
            pressure_inhg: 29.8
        },
        standardClub: "8-Iron",
        adjustedClub: "9-Iron (aim 5yds left)",
        explanation: "In 105°F heat, air density drops significantly - your ball experiences <strong>less drag and flies further</strong>. Add the 1,500 feet of desert elevation and bone-dry 12% humidity, and you're playing in ideal distance conditions. <strong>Club down to a 9-iron</strong>. The left-to-right crosswind will push your ball, so aim at the left edge of the green. Expect a <strong>penetrating ball flight</strong> in the thin air."
    },
    {
        id: 3,
        title: "St Andrews #11 - Scottish Links",
        description: "The 172-yard par 3 at the Home of Golf. Scottish links golf means battling unpredictable winds, firm turf, and run-out that can double your carry distance.",
        shot: {
            ball_speed_mph: 110,
            launch_angle_deg: 16,
            spin_rate_rpm: 5500,
            spin_axis_deg: -3,
            direction_deg: 0
        },
        conditions: {
            wind_speed_mph: 22,
            wind_direction_deg: 315,
            temperature_f: 52,
            altitude_ft: 30,
            humidity_pct: 85,
            pressure_inhg: 29.7
        },
        standardClub: "6-Iron",
        adjustedClub: "5-Iron (punch, aim 15yds right)",
        explanation: "The 22 mph quartering wind is the dominant factor, and Scottish winds are never steady. The cold, dense sea-level air adds drag, while high humidity slightly offsets this. <strong>Take more club (5-iron)</strong> and hit a low punch shot to reduce wind effect. Aim well right of target - the wind will push your ball left. On firm links turf, expect <strong>significant run-out</strong> after landing."
    },
    {
        id: 4,
        title: "Bethpage Black #17 - Cold Morning",
        description: "A brutal 207-yard par 3 in early morning conditions. When temps drop to 45°F, the dense air makes this already long hole play even longer.",
        shot: {
            ball_speed_mph: 130,
            launch_angle_deg: 14,
            spin_rate_rpm: 4500,
            spin_axis_deg: 0,
            direction_deg: 0
        },
        conditions: {
            wind_speed_mph: 10,
            wind_direction_deg: 0,
            temperature_f: 45,
            altitude_ft: 90,
            humidity_pct: 70,
            pressure_inhg: 30.2
        },
        standardClub: "4-Iron",
        adjustedClub: "3-Hybrid (full send)",
        explanation: "Cold air is <strong>dense air</strong>, and 45°F mornings add significant drag to your ball flight. The 10 mph headwind compounds this, knocking even more distance off your shot. At near sea level with high pressure, you're fighting maximum air resistance. <strong>Club way up to a 3-hybrid</strong> - the cold and wind together could cost you 15-20 yards compared to a summer afternoon."
    },
    {
        id: 5,
        title: "Bandon Dunes #12 - Oregon Coast",
        description: "A 145-yard par 3 perched on dramatic cliffs above the Pacific. Oregon coast weather is notoriously unpredictable, with wind, mist, and rapid temperature changes.",
        shot: {
            ball_speed_mph: 100,
            launch_angle_deg: 25,
            spin_rate_rpm: 7500,
            spin_axis_deg: -2,
            direction_deg: 0
        },
        conditions: {
            wind_speed_mph: 18,
            wind_direction_deg: 270,
            temperature_f: 58,
            altitude_ft: 100,
            humidity_pct: 90,
            pressure_inhg: 29.9
        },
        standardClub: "9-Iron",
        adjustedClub: "8-Iron (low draw, aim 12yds right)",
        explanation: "The right-to-left 18 mph wind off the Pacific will move your ball significantly. Cool temperatures and high humidity create dense, heavy air. <strong>Club up to an 8-iron</strong> and play a low draw - starting right and letting the wind bring it back. The high spin will help the ball hold on the green despite the shallower landing angle. Trust the wind to do the work."
    }
];

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
        // Call API
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

    // Standard stats
    document.getElementById('std-carry').textContent = Math.round(baseline.carry_yards);
    document.getElementById('std-total').textContent = Math.round(baseline.total_yards);
    document.getElementById('std-apex').textContent = Math.round(baseline.apex_height_yards);
    document.getElementById('std-drift').textContent = Math.round(baseline.lateral_drift_yards);
    document.getElementById('std-flight').textContent = baseline.flight_time_seconds.toFixed(1);
    document.getElementById('std-land').textContent = Math.round(baseline.landing_angle_deg) + '°';
    document.getElementById('std-club').textContent = scenario.standardClub;

    // Adjusted stats
    document.getElementById('adj-carry').textContent = Math.round(adjusted.carry_yards);
    document.getElementById('adj-total').textContent = Math.round(adjusted.total_yards);
    document.getElementById('adj-apex').textContent = Math.round(adjusted.apex_height_yards);
    document.getElementById('adj-drift').textContent = Math.round(Math.abs(adjusted.lateral_drift_yards));
    document.getElementById('adj-flight').textContent = adjusted.flight_time_seconds.toFixed(1);
    document.getElementById('adj-land').textContent = Math.round(adjusted.landing_angle_deg) + '°';
    document.getElementById('adj-club').textContent = scenario.adjustedClub;

    // Deltas
    updateDelta('delta-carry', adjusted.carry_yards - baseline.carry_yards);
    updateDelta('delta-total', adjusted.total_yards - baseline.total_yards);
    updateDelta('delta-apex', adjusted.apex_height_yards - baseline.apex_height_yards);
    updateDelta('delta-drift', adjusted.lateral_drift_yards - baseline.lateral_drift_yards, true);
    updateDelta('delta-flight', adjusted.flight_time_seconds - baseline.flight_time_seconds);
    updateDelta('delta-land', adjusted.landing_angle_deg - baseline.landing_angle_deg, false, '°');

    // Conditions pills
    document.getElementById('cond-temp').textContent = `🌡️ ${conditions.temperature_f}°F`;
    document.getElementById('cond-wind').textContent = `💨 ${conditions.wind_speed_mph} mph ${getWindDirectionText(conditions.wind_direction_deg)}`;
    document.getElementById('cond-altitude').textContent = `⛰️ ${conditions.altitude_ft.toLocaleString()} ft elevation`;
    document.getElementById('cond-humidity').textContent = `💧 ${conditions.humidity_pct}% humidity`;

    // Impact breakdown
    updateImpactBar('wind', impact.wind_effect_yards);
    updateImpactBar('temp', impact.temperature_effect_yards);
    updateImpactBar('altitude', impact.altitude_effect_yards);
    updateImpactBar('humidity', impact.humidity_effect_yards);

    // Explanation
    document.getElementById('explanation-text').innerHTML = scenario.explanation;
}

// Helper: Update delta display
function updateDelta(id, value, absolute = false, suffix = '') {
    const el = document.getElementById(id);
    const displayValue = absolute ? Math.abs(value) : value;
    const sign = value >= 0 ? '+' : '';
    el.textContent = `${sign}${displayValue.toFixed(1)}${suffix}`;
    el.className = 'stat-delta ' + (value < 0 ? 'negative' : value > 0 ? 'positive' : '');
}

// Helper: Update impact bar
function updateImpactBar(type, value) {
    const bar = document.getElementById(`bar-${type}`);
    const valueEl = document.getElementById(`impact-${type}`);

    const maxEffect = 15; // Max yards for full bar
    const width = Math.min(Math.abs(value) / maxEffect * 100, 100);

    bar.style.width = `${width}%`;
    bar.className = `impact-bar ${value < 0 ? 'negative' : 'positive'}`;

    const sign = value >= 0 ? '+' : '';
    valueEl.textContent = `${sign}${value.toFixed(1)} yds`;
}

// Helper: Get wind direction text
function getWindDirectionText(deg) {
    if (deg >= 337.5 || deg < 22.5) return 'headwind';
    if (deg >= 22.5 && deg < 67.5) return 'front-left';
    if (deg >= 67.5 && deg < 112.5) return 'L-to-R';
    if (deg >= 112.5 && deg < 157.5) return 'back-left';
    if (deg >= 157.5 && deg < 202.5) return 'tailwind';
    if (deg >= 202.5 && deg < 247.5) return 'back-right';
    if (deg >= 247.5 && deg < 292.5) return 'R-to-L';
    if (deg >= 292.5 && deg < 337.5) return 'front-right';
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

// Setup slider listeners
function setupSliderListeners() {
    const sliders = [
        { id: 'ball-speed', suffix: '' },
        { id: 'launch-angle', suffix: '°' },
        { id: 'spin-rate', suffix: '' },
        { id: 'temperature', suffix: '°F' },
        { id: 'wind-speed', suffix: ' mph' },
        { id: 'altitude', suffix: ' ft' },
        { id: 'humidity', suffix: '%' }
    ];

    sliders.forEach(slider => {
        const input = document.getElementById(slider.id);
        const display = document.getElementById(`${slider.id}-val`);

        if (input && display) {
            input.addEventListener('input', () => {
                display.textContent = input.value + (slider.suffix || '');
            });
        }
    });
}

// Simulate custom scenario
async function simulateCustom() {
    const shot = {
        ball_speed_mph: parseFloat(document.getElementById('ball-speed').value),
        launch_angle_deg: parseFloat(document.getElementById('launch-angle').value),
        spin_rate_rpm: parseFloat(document.getElementById('spin-rate').value),
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

    // Update header for custom scenario
    document.getElementById('scenario-title').textContent = 'Custom Scenario';
    document.getElementById('scenario-description').textContent =
        `Ball Speed: ${shot.ball_speed_mph} mph | Launch: ${shot.launch_angle_deg}° | Spin: ${shot.spin_rate_rpm} rpm`;

    showLoading();

    try {
        const response = await fetch(`${API_BASE}/v1/trajectory`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ shot, conditions })
        });

        if (!response.ok) throw new Error('API request failed');

        const data = await response.json();

        // Create a custom scenario object for display
        const customScenario = {
            conditions,
            standardClub: getClubFromDistance(data.baseline.carry_yards),
            adjustedClub: getClubFromDistance(data.adjusted.carry_yards) + getAdjustmentNote(data),
            explanation: generateCustomExplanation(data)
        };

        updateDisplay(data, customScenario);
        hideCustomPanel();
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to calculate trajectory. Please try again.');
    } finally {
        hideLoading();
    }
}

// Helper: Estimate club from distance
function getClubFromDistance(yards) {
    if (yards >= 200) return 'Driver';
    if (yards >= 180) return '3-Wood';
    if (yards >= 170) return '3-Hybrid';
    if (yards >= 160) return '4-Iron';
    if (yards >= 150) return '5-Iron';
    if (yards >= 140) return '6-Iron';
    if (yards >= 130) return '7-Iron';
    if (yards >= 120) return '8-Iron';
    if (yards >= 110) return '9-Iron';
    if (yards >= 100) return 'PW';
    if (yards >= 85) return 'GW';
    if (yards >= 70) return 'SW';
    return 'LW';
}

// Helper: Get adjustment note based on drift
function getAdjustmentNote(data) {
    const drift = data.adjusted.lateral_drift_yards;
    if (Math.abs(drift) < 3) return '';
    const direction = drift > 0 ? 'left' : 'right';
    return ` (aim ${Math.abs(Math.round(drift))}yds ${direction})`;
}

// Helper: Generate explanation for custom scenario
function generateCustomExplanation(data) {
    const impact = data.impact_breakdown;
    const parts = [];

    if (Math.abs(impact.wind_effect_yards) > 2) {
        const effect = impact.wind_effect_yards < 0 ? 'costing' : 'adding';
        parts.push(`Wind is ${effect} you <strong>${Math.abs(impact.wind_effect_yards).toFixed(1)} yards</strong>`);
    }

    if (Math.abs(impact.temperature_effect_yards) > 1) {
        const effect = impact.temperature_effect_yards < 0 ? 'reducing' : 'adding';
        parts.push(`Temperature is ${effect} <strong>${Math.abs(impact.temperature_effect_yards).toFixed(1)} yards</strong>`);
    }

    if (Math.abs(impact.altitude_effect_yards) > 1) {
        parts.push(`Altitude adds <strong>${impact.altitude_effect_yards.toFixed(1)} yards</strong> due to thinner air`);
    }

    if (Math.abs(data.adjusted.lateral_drift_yards) > 3) {
        const direction = data.adjusted.lateral_drift_yards > 0 ? 'right' : 'left';
        parts.push(`Expect <strong>${Math.abs(data.adjusted.lateral_drift_yards).toFixed(1)} yards</strong> of ${direction} drift`);
    }

    const total = impact.total_adjustment_yards;
    const netEffect = total >= 0 ? 'longer' : 'shorter';
    parts.push(`<strong>Net effect: ${Math.abs(total).toFixed(1)} yards ${netEffect}</strong> than standard conditions`);

    return parts.join('. ') + '.';
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

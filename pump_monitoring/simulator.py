"""Synthetic pump telemetry generator for algorithm and dashboard demonstrations.

Fault patterns are deliberately simplified teaching scenarios, not validated
physical signatures for a specific pump, motor, installation or sensor.
"""
from datetime import datetime, timedelta, timezone
import random

FEATURES = [
    "vibration_rms_mm_s", "bearing_temp_c", "motor_current_a",
    "flow_m3_h", "discharge_pressure_bar", "rpm"
]
SCENARIOS = ["normal", "bearing_wear", "misalignment", "cavitation", "overload", "low_flow"]


def _clip(value: float, low: float, high: float) -> float:
    return min(high, max(low, value))


def sample_scenario(scenario: str, rng: random.Random) -> dict[str, float]:
    if scenario == "normal":
        values = [rng.gauss(1.7, 0.28), rng.gauss(55, 3.5), rng.gauss(8.0, 0.55),
                  rng.gauss(30, 1.8), rng.gauss(3.2, 0.18), rng.gauss(1450, 12)]
    elif scenario == "bearing_wear":
        values = [rng.gauss(5.0, 0.65), rng.gauss(69, 4), rng.gauss(8.6, 0.65),
                  rng.gauss(29, 2), rng.gauss(3.1, 0.2), rng.gauss(1445, 18)]
    elif scenario == "misalignment":
        values = [rng.gauss(6.2, 0.7), rng.gauss(65, 4), rng.gauss(9.5, 0.7),
                  rng.gauss(28.5, 2), rng.gauss(3.0, 0.2), rng.gauss(1435, 20)]
    elif scenario == "cavitation":
        values = [rng.gauss(4.6, 0.7), rng.gauss(60, 4), rng.gauss(7.5, 0.7),
                  rng.gauss(22, 2.5), rng.gauss(2.2, 0.3), rng.gauss(1440, 20)]
    elif scenario == "overload":
        values = [rng.gauss(3.4, 0.5), rng.gauss(78, 4), rng.gauss(13.0, 0.9),
                  rng.gauss(31, 2), rng.gauss(3.4, 0.25), rng.gauss(1430, 18)]
    elif scenario == "low_flow":
        values = [rng.gauss(2.8, 0.45), rng.gauss(61, 4), rng.gauss(6.4, 0.6),
                  rng.gauss(12, 2.0), rng.gauss(1.8, 0.25), rng.gauss(1450, 15)]
    else:
        raise ValueError(f"Unknown scenario: {scenario}")
    return {
        FEATURES[0]: round(_clip(values[0], 0, 100), 3),
        FEATURES[1]: round(_clip(values[1], -20, 250), 2),
        FEATURES[2]: round(_clip(values[2], 0, 1000), 3),
        FEATURES[3]: round(_clip(values[3], 0, 10000), 3),
        FEATURES[4]: round(_clip(values[4], 0, 100), 3),
        FEATURES[5]: round(_clip(values[5], 0, 30000), 2),
    }


def generate_labeled_dataset(n_per_scenario: int = 500, seed: int = 42):
    if n_per_scenario < 10:
        raise ValueError("n_per_scenario must be at least 10")
    rng = random.Random(seed)
    rows = []
    for scenario in SCENARIOS:
        for _ in range(n_per_scenario):
            row = sample_scenario(scenario, rng)
            row["scenario"] = scenario
            rows.append(row)
    rng.shuffle(rows)
    return rows


def generate_reading(index: int, *, seed: int = 42, scenario: str | None = None, start=None):
    rng = random.Random(seed + index)
    if scenario is None:
        # Cycle through normal operation and occasional artificial fault scenarios.
        cycle = ["normal"] * 8 + ["bearing_wear", "misalignment", "cavitation", "overload", "low_flow"]
        scenario = cycle[index % len(cycle)]
    start = start or datetime.now(timezone.utc) - timedelta(minutes=5 * 100)
    data = sample_scenario(scenario, rng)
    data.update({
        "timestamp": start + timedelta(minutes=5 * index),
        "asset_id": "pump-demo-01",
        "scenario": scenario,  # synthetic ground-truth label for demo evaluation only
    })
    return data


def generate_readings(count: int = 200, seed: int = 42):
    if count < 1:
        raise ValueError("count must be at least 1")
    start = datetime.now(timezone.utc) - timedelta(minutes=5 * count)
    for index in range(count):
        yield generate_reading(index, seed=seed, start=start)

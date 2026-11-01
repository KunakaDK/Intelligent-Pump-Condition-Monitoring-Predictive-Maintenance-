import pytest
from pump_monitoring.simulator import generate_reading, generate_labeled_dataset, generate_readings, FEATURES
from pump_monitoring.detector import PumpFaultDetector
from pump_monitoring.storage import PumpStore
from pump_monitoring.service import PumpService


def test_simulator_produces_expected_features():
    reading = generate_reading(3, seed=123, scenario="normal")
    assert set(FEATURES).issubset(reading)
    assert reading["vibration_rms_mm_s"] >= 0
    assert reading["rpm"] > 0


def test_dataset_contains_all_synthetic_scenarios():
    rows = generate_labeled_dataset(n_per_scenario=10)
    assert len(rows) == 60
    assert {r["scenario"] for r in rows} == {"normal", "bearing_wear", "misalignment", "cavitation", "overload", "low_flow"}


def test_zero_count_rejected():
    with pytest.raises(ValueError):
        list(generate_readings(0))


def test_detector_trains_predicts_and_persists(tmp_path):
    path = tmp_path / "model.joblib"
    detector = PumpFaultDetector(path)
    metrics = detector.train(n_per_scenario=30)
    assert 0.0 <= metrics["accuracy_on_synthetic_holdout"] <= 1.0
    reading = generate_reading(4, scenario="normal")
    condition, score, explanation = detector.predict(reading)
    assert condition in {"normal", "bearing_wear", "misalignment", "cavitation", "overload", "low_flow"}
    assert 0 <= score <= 1
    assert explanation
    assert path.exists()
    reloaded = PumpFaultDetector(path)
    assert reloaded.predict(reading)[0] == condition


def test_store_and_service(tmp_path):
    store = PumpStore(tmp_path / "pump.db")
    detector = PumpFaultDetector(tmp_path / "model.joblib")
    service = PumpService(store, detector)
    reading = generate_reading(10, scenario="bearing_wear")
    result = service.ingest(reading)
    rows = store.list(5)
    assert result["id"] == 1
    assert len(rows) == 1
    assert rows[0]["asset_id"] == "pump-demo-01"
    assert rows[0]["predicted_condition"] == result["predicted_condition"]


def test_api_end_to_end(tmp_path):
    from fastapi.testclient import TestClient
    from pump_monitoring.api import create_app

    client = TestClient(create_app(str(tmp_path / "api.db"), str(tmp_path / "api-model.joblib")))
    assert client.get("/health").status_code == 200
    payload = {
        "asset_id": "api-test", "vibration_rms_mm_s": 1.7,
        "bearing_temp_c": 55, "motor_current_a": 8.0,
        "flow_m3_h": 30, "discharge_pressure_bar": 3.2, "rpm": 1450,
    }
    response = client.post("/telemetry", json=payload)
    assert response.status_code == 200
    assert response.json()["predicted_condition"] == "normal"
    assert client.get("/telemetry").json()[0]["asset_id"] == "api-test"
    assert client.get("/summary").json()["records"] == 1

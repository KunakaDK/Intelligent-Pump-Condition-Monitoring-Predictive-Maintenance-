# Intelligent Pump Condition Monitoring & Predictive Maintenance

**Personal portfolio project | Simulation-based | Monitoring-only**

A complete demonstration of an equipment-monitoring pipeline for a *simulated* water-pumping asset. It generates sensor telemetry, trains a multi-class Random Forest classifier on synthetic operating scenarios, exposes inference through FastAPI, persists readings in SQLite, and displays equipment trends and model classifications in Streamlit.

> **Important limitation:** all training and demo telemetry are synthetic. The model recognises simplified patterns created by this repository; its metrics are not evidence of real pump-fault diagnostic performance. It is not validated for a particular pump, motor, site or sensor. This application is monitoring-only and does not control physical equipment.

## Features

- Synthetic healthy and abnormal scenarios: normal, bearing-wear-like, misalignment-like, cavitation-like, overload and low-flow.
- Telemetry variables: vibration RMS, bearing temperature, motor current, flow, discharge pressure and rotational speed.
- Reproducible training of a Random Forest classifier with a held-out synthetic test split.
- FastAPI endpoint for telemetry ingestion and classification.
- SQLite persistence of readings and predictions.
- Streamlit dashboard with trends, condition counts, severity labels and explanations.
- Tests for simulator, dataset classes, detector training, persistence and service ingestion.

## Architecture

```text
Synthetic labelled scenario generator
             |
       Train/test split
             |
      Random Forest model
             |
Synthetic telemetry stream
             |
         FastAPI
             |
  feature inference + model
             |
           SQLite
             |
      Streamlit dashboard
```

## Requirements

- Python 3.10 or newer.
- Install dependencies from `requirements.txt`.

## Setup

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

## 1. Train the demonstration model

```bash
python -m pump_monitoring.train_model
```

This creates:

- `models/pump_fault_classifier.joblib`
- `models/pump_fault_classifier.metrics.json`

The metrics file reports performance on a held-out split from the same synthetic scenario generator. Do not describe it as field accuracy.

## 2. Generate and store demo telemetry

```bash
python -m pump_monitoring.cli seed --count 240 --clear
```

The generator cycles through normal and artificial fault scenarios. The scenario label is used only by the simulator; it is not submitted as a model input.

## 3. Start API

```bash
uvicorn pump_monitoring.api:app --reload --port 8001
```

API documentation: `http://127.0.0.1:8001/docs`.

## 4. Start dashboard

In another terminal:

```bash
streamlit run pump_monitoring/dashboard.py
```

The dashboard defaults to `http://127.0.0.1:8001`. Set `PUMP_API_URL` to override it.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | API and model health |
| POST | `/telemetry` | Validate, classify and store a reading |
| GET | `/telemetry?limit=200` | Retrieve recent readings and predictions |
| GET | `/summary` | Aggregate monitoring statistics |

Example input:

```json
{
  "timestamp": "2026-01-01T12:00:00Z",
  "asset_id": "pump-demo-01",
  "vibration_rms_mm_s": 1.8,
  "bearing_temp_c": 55.0,
  "motor_current_a": 8.1,
  "flow_m3_h": 30.0,
  "discharge_pressure_bar": 3.2,
  "rpm": 1450
}
```

## Tests

```bash
pytest -q
```

## Suggested CV description (only after running and verifying the project)

**Prototype de surveillance conditionnelle d'un système de pompage (données simulées)** – Développement d'une chaîne de monitoring intégrant génération de télémétrie, apprentissage d'un modèle Random Forest sur des scénarios synthétiques, API FastAPI, stockage SQLite et tableau de bord Streamlit pour l'analyse des vibrations, de la température, du courant, du débit et de la pression.

## Engineering notes

- The synthetic fault patterns are educational abstractions and are not specific to a real pump or manufacturer.
- A real predictive-maintenance deployment requires labelled field data, sensor selection and calibration, domain-engineer review, validation across operating regimes, and monitoring for model drift.
- Never use this classifier as the sole basis for maintenance, safety or equipment shutdown decisions.
- No actuator control or commands to a physical pump are implemented.

A small synthetic SQLite demo database is included in the downloadable archive so the dashboard can show sample trends immediately. To regenerate it, run the seed command above. The database is ignored by Git by default; seed it after cloning.

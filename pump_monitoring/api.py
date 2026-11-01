import os
from fastapi import FastAPI, Query
from .schemas import PumpTelemetry, PumpTelemetryOut
from .storage import PumpStore
from .detector import PumpFaultDetector
from .service import PumpService


def create_app(db_path: str | None = None, model_path: str | None = None) -> FastAPI:
    store = PumpStore(db_path or os.getenv("PUMP_DB_PATH", "./data/pump_monitor.db"))
    detector = PumpFaultDetector(model_path or os.getenv("PUMP_MODEL_PATH", "./models/pump_fault_classifier.joblib"))
    service = PumpService(store, detector)
    app = FastAPI(title="Pump Condition Monitoring API", version="1.0.0",
                  description="Simulation-based predictive-maintenance demonstration; not a validated diagnostic system.")
    app.state.store = store
    app.state.service = service

    @app.get("/health")
    def health():
        return {"status": "ok", "mode": "simulation-only", "model_loaded": detector.model is not None}

    @app.post("/telemetry")
    def ingest(reading: PumpTelemetry):
        return service.ingest(reading.model_dump())

    @app.get("/telemetry", response_model=list[PumpTelemetryOut])
    def list_telemetry(limit: int = Query(default=200, ge=1, le=5000)):
        return store.list(limit)

    @app.get("/summary")
    def summary():
        return store.summary()

    return app


app = create_app()

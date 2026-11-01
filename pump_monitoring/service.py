from .storage import PumpStore
from .detector import PumpFaultDetector


class PumpService:
    def __init__(self, store: PumpStore, detector: PumpFaultDetector):
        self.store = store
        self.detector = detector

    def ingest(self, reading: dict) -> dict:
        condition, anomaly_score, explanation = self.detector.predict(reading)
        severity = "normal" if condition == "normal" else ("high" if condition in {"overload", "cavitation"} else "warning")
        record = {**reading, "predicted_condition": condition, "anomaly_score": anomaly_score,
                  "severity": severity, "explanation": explanation}
        row_id = self.store.insert(record)
        return {"id": row_id, "predicted_condition": condition, "anomaly_score": anomaly_score,
                "severity": severity, "explanation": explanation}

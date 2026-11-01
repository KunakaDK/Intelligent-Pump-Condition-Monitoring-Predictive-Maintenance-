"""Train and persist the synthetic-scenario demonstration classifier."""
import json
import os
from pathlib import Path
from .detector import PumpFaultDetector


def main():
    path = Path(os.getenv("PUMP_MODEL_PATH", "./models/pump_fault_classifier.joblib"))
    detector = PumpFaultDetector(path)
    metrics = detector.train(n_per_scenario=600, seed=42)
    metrics_path = path.with_suffix(".metrics.json")
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(f"Model saved to: {path}")
    print(f"Metrics saved to: {metrics_path}")
    print(f"Synthetic holdout accuracy: {metrics['accuracy_on_synthetic_holdout']:.3f}")
    print("This metric measures only separation of generated scenarios; it is not field performance.")


if __name__ == "__main__":
    main()

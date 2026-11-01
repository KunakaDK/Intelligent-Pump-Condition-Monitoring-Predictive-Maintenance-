import argparse
import json
import os
from .simulator import generate_readings
from .storage import PumpStore
from .detector import PumpFaultDetector
from .service import PumpService


def main():
    parser = argparse.ArgumentParser(description="Pump monitoring demo utilities")
    sub = parser.add_subparsers(dest="command", required=True)
    seed = sub.add_parser("seed", help="Insert synthetic pump readings")
    seed.add_argument("--count", type=int, default=240)
    seed.add_argument("--clear", action="store_true")
    train = sub.add_parser("train", help="Train classifier on generated synthetic scenarios")
    train.add_argument("--per-class", type=int, default=500)
    args = parser.parse_args()
    if args.command == "train":
        detector = PumpFaultDetector(os.getenv("PUMP_MODEL_PATH", "./models/pump_fault_classifier.joblib"))
        metrics = detector.train(args.per_class)
        print(json.dumps(metrics, indent=2))
        return
    store = PumpStore(os.getenv("PUMP_DB_PATH", "./data/pump_monitor.db"))
    if args.clear:
        store.clear()
    detector = PumpFaultDetector(os.getenv("PUMP_MODEL_PATH", "./models/pump_fault_classifier.joblib"))
    service = PumpService(store, detector)
    counts = {}
    for reading in generate_readings(args.count):
        reading.pop("scenario", None)  # labels are not sent to the inference API/model
        result = service.ingest(reading)
        counts[result["predicted_condition"]] = counts.get(result["predicted_condition"], 0) + 1
    print(json.dumps({"inserted": args.count, "predicted_conditions": counts, "database": store.db_path}, indent=2))


if __name__ == "__main__":
    main()

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

FIELDS = [
    "timestamp", "asset_id", "vibration_rms_mm_s", "bearing_temp_c", "motor_current_a",
    "flow_m3_h", "discharge_pressure_bar", "rpm", "predicted_condition", "anomaly_score", "severity", "explanation"
]


class PumpStore:
    def __init__(self, db_path: str | Path = "./data/pump_monitor.db"):
        self.db_path = str(db_path)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def initialize(self):
        with self.connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pump_readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    asset_id TEXT NOT NULL,
                    vibration_rms_mm_s REAL NOT NULL,
                    bearing_temp_c REAL NOT NULL,
                    motor_current_a REAL NOT NULL,
                    flow_m3_h REAL NOT NULL,
                    discharge_pressure_bar REAL NOT NULL,
                    rpm REAL NOT NULL,
                    predicted_condition TEXT NOT NULL,
                    anomaly_score REAL NOT NULL,
                    severity TEXT NOT NULL,
                    explanation TEXT NOT NULL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_pump_timestamp ON pump_readings(timestamp)")

    def insert(self, reading: dict[str, Any]) -> int:
        data = dict(reading)
        if isinstance(data["timestamp"], datetime):
            data["timestamp"] = data["timestamp"].isoformat()
        placeholders = ",".join("?" for _ in FIELDS)
        values = [data[f] for f in FIELDS]
        with self.connect() as conn:
            cur = conn.execute(f"INSERT INTO pump_readings ({','.join(FIELDS)}) VALUES ({placeholders})", values)
            return int(cur.lastrowid)

    def list(self, limit: int = 200):
        limit = max(1, min(int(limit), 5000))
        with self.connect() as conn:
            rows = conn.execute("SELECT * FROM pump_readings ORDER BY timestamp DESC, id DESC LIMIT ?", (limit,)).fetchall()
        return [dict(r) for r in rows]

    def summary(self):
        with self.connect() as conn:
            row = conn.execute("""
                SELECT COUNT(*) AS records, MAX(timestamp) AS latest_timestamp,
                       AVG(vibration_rms_mm_s) AS avg_vibration,
                       AVG(bearing_temp_c) AS avg_temperature,
                       AVG(motor_current_a) AS avg_current,
                       SUM(CASE WHEN severity != 'normal' THEN 1 ELSE 0 END) AS flagged_records
                FROM pump_readings
            """).fetchone()
        return dict(row)

    def clear(self):
        with self.connect() as conn:
            conn.execute("DELETE FROM pump_readings")

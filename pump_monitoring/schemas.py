from datetime import datetime, timezone
from pydantic import BaseModel, ConfigDict, Field


class PumpTelemetry(BaseModel):
    """Validated sensor payload; operating ranges are demo constraints only."""
    model_config = ConfigDict(extra="forbid")

    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    asset_id: str = Field(default="pump-demo-01", min_length=1, max_length=64)
    vibration_rms_mm_s: float = Field(ge=0, le=100)
    bearing_temp_c: float = Field(ge=-20, le=250)
    motor_current_a: float = Field(ge=0, le=1000)
    flow_m3_h: float = Field(ge=0, le=10000)
    discharge_pressure_bar: float = Field(ge=0, le=100)
    rpm: float = Field(ge=0, le=30000)


class PumpTelemetryOut(PumpTelemetry):
    id: int
    predicted_condition: str
    anomaly_score: float
    severity: str
    explanation: str

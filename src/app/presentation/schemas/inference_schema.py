from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.risk_level import RiskLevel


class VitalRecord(BaseModel):
    recorded_at: datetime
    vitals: dict[str, float]


class InferenceRequest(BaseModel):
    patient_id: str
    records: list[VitalRecord] = Field(..., min_length=1)


class InferenceResponse(BaseModel):
    patient_id: str
    risk_score: float
    risk_level: RiskLevel
    checked_rules: list[str]
    evaluated_at: datetime

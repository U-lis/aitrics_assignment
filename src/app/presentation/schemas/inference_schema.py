from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.risk_level import RiskLevel


class VitalRecord(BaseModel):
    """Single time-point vital measurements for inference."""

    recorded_at: datetime = Field(
        ...,
        description="Timestamp when these vitals were recorded (ISO 8601 format)",
        examples=["2025-12-01T10:15:00Z"],
    )
    vitals: dict[str, float] = Field(
        ...,
        description="Dictionary mapping vital type to measured value (e.g., HR, SBP, SpO2)",
        examples=[{"HR": 130.0, "SBP": 85.0, "SpO2": 89.0}],
    )


class InferenceRequest(BaseModel):
    """Request body for vital risk evaluation."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "patient_id": "P00001234",
                    "records": [
                        {
                            "recorded_at": "2025-12-01T10:15:00Z",
                            "vitals": {"HR": 130.0, "SBP": 85.0, "SpO2": 89.0},
                        }
                    ],
                }
            ]
        },
    )

    patient_id: str = Field(
        ...,
        description="Hospital patient identifier",
        examples=["P00001234"],
    )
    records: list[VitalRecord] = Field(
        ...,
        min_length=1,
        description="List of vital records to evaluate (minimum 1 record required)",
    )


class InferenceResponse(BaseModel):
    """Response body containing risk assessment result."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "patient_id": "P00001234",
                    "risk_score": 0.91,
                    "risk_level": "HIGH",
                    "checked_rules": ["HR > 120", "SBP < 90", "SpO2 < 90"],
                    "evaluated_at": "2025-12-01T10:20:00Z",
                }
            ]
        },
    )

    patient_id: str = Field(..., description="Hospital patient identifier")
    risk_score: float = Field(
        ...,
        description="Calculated risk score (0.0 to 1.0)",
        ge=0.0,
        le=1.0,
    )
    risk_level: RiskLevel = Field(
        ...,
        description="Risk category: LOW (score <= 0.3), MEDIUM (0.4-0.7), HIGH (>= 0.8)",
    )
    checked_rules: list[str] = Field(
        ...,
        description="List of triggered risk rules (e.g., 'HR > 120', 'SBP < 90')",
    )
    evaluated_at: datetime = Field(..., description="Timestamp of evaluation (UTC)")

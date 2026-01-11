from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.vital_type import VitalType


class VitalCreateRequest(BaseModel):
    """Request body for recording a vital sign measurement."""

    patient_id: str = Field(
        ...,
        description="Hospital patient identifier",
        examples=["P00001234"],
    )
    recorded_at: datetime = Field(
        ...,
        description="When the vital sign was recorded (ISO 8601 datetime with timezone)",
        examples=["2025-12-01T10:15:00Z"],
    )
    vital_type: VitalType = Field(
        ...,
        description="Type of vital sign: HR (bpm), RR (breaths/min), SBP/DBP (mmHg), SpO2 (%), BT (Celsius)",
        examples=["HR"],
    )
    value: float = Field(
        ...,
        description="Measured value (unit depends on vital_type)",
        examples=[110.0],
    )


class VitalUpdateRequest(BaseModel):
    """Request body for correcting a vital record."""

    value: float = Field(
        ...,
        description="Corrected measurement value",
        examples=[115.0],
    )
    vital_type: VitalType = Field(
        ...,
        description="Type of vital sign: HR (bpm), RR (breaths/min), SBP/DBP (mmHg), SpO2 (%), BT (Celsius)",
        examples=["HR"],
    )
    version: int = Field(
        ...,
        description="Current version number for optimistic locking. Must match the server's version.",
        examples=[1],
    )


class VitalResponse(BaseModel):
    """Response body containing vital record information."""

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "patient_id": "P00001234",
                    "recorded_at": "2025-12-01T10:15:00Z",
                    "vital_type": "HR",
                    "value": 110.0,
                    "version": 1,
                    "created_at": "2025-12-01T10:15:00Z",
                    "updated_at": "2025-12-01T10:15:00Z",
                }
            ]
        },
    )

    id: UUID = Field(..., description="Internal unique identifier (UUID)")
    patient_id: str = Field(..., description="Hospital patient identifier")
    recorded_at: datetime = Field(
        ..., description="When the vital sign was recorded"
    )
    vital_type: str = Field(..., description="Type of vital sign")
    value: float = Field(..., description="Measured value")
    version: int = Field(
        ..., description="Version number for optimistic locking"
    )
    created_at: datetime = Field(..., description="Record creation timestamp (UTC)")
    updated_at: datetime = Field(..., description="Last update timestamp (UTC)")


class VitalItem(BaseModel):
    """Single vital measurement in a list response."""

    recorded_at: datetime = Field(
        ...,
        description="When the vital sign was recorded",
        examples=["2025-12-01T10:15:00Z"],
    )
    value: float = Field(
        ...,
        description="Measured value",
        examples=[110.0],
    )


class VitalListResponse(BaseModel):
    """Response body for vital records query."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "patient_id": "P00001234",
                    "vital_type": "HR",
                    "items": [
                        {"recorded_at": "2025-12-01T10:15:00Z", "value": 110.0},
                        {"recorded_at": "2025-12-01T10:30:00Z", "value": 108.0},
                    ],
                }
            ]
        },
    )

    patient_id: str = Field(..., description="Hospital patient identifier")
    vital_type: str | None = Field(
        ...,
        description="Vital type filter applied (null if no filter)",
    )
    items: list[VitalItem] = Field(
        ..., description="List of vital measurements"
    )

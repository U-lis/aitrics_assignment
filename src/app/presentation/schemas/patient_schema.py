from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PatientCreateRequest(BaseModel):
    """Request body for registering a new patient."""

    patient_id: str = Field(
        ...,
        description="Hospital patient identifier",
        examples=["P00001234"],
    )
    name: str = Field(
        ...,
        description="Patient full name",
        examples=["Hong Gil-dong"],
    )
    gender: Literal["M", "F"] = Field(
        ...,
        description="Patient gender: 'M' for male, 'F' for female",
        examples=["M"],
    )
    birth_date: date = Field(
        ...,
        description="Patient date of birth (YYYY-MM-DD)",
        examples=["1975-03-01"],
    )


class PatientUpdateRequest(BaseModel):
    """Request body for updating patient information."""

    name: str = Field(
        ...,
        description="Patient full name",
        examples=["Hong Gil-dong"],
    )
    gender: Literal["M", "F"] = Field(
        ...,
        description="Patient gender: 'M' for male, 'F' for female",
        examples=["M"],
    )
    birth_date: date = Field(
        ...,
        description="Patient date of birth (YYYY-MM-DD)",
        examples=["1975-03-01"],
    )
    version: int = Field(
        ...,
        description="Current version number for optimistic locking. Must match the server's version.",
        examples=[1],
    )


class PatientResponse(BaseModel):
    """Response body containing patient information."""

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "patient_id": "P00001234",
                    "name": "Hong Gil-dong",
                    "gender": "M",
                    "birth_date": "1975-03-01",
                    "version": 1,
                    "created_at": "2025-12-01T10:00:00Z",
                    "updated_at": "2025-12-01T10:00:00Z",
                }
            ]
        },
    )

    id: UUID = Field(..., description="Internal unique identifier (UUID)")
    patient_id: str = Field(..., description="Hospital patient identifier")
    name: str = Field(..., description="Patient full name")
    gender: str = Field(..., description="Patient gender: 'M' or 'F'")
    birth_date: date = Field(..., description="Patient date of birth")
    version: int = Field(
        ..., description="Version number for optimistic locking"
    )
    created_at: datetime = Field(..., description="Record creation timestamp (UTC)")
    updated_at: datetime = Field(..., description="Last update timestamp (UTC)")

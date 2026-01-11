from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.vital_service import VitalService
from app.dependencies import verify_bearer_token
from app.domain.vital_type import VitalType
from app.infrastructure.database import get_db_session
from app.presentation.schemas.error_schema import ErrorResponse
from app.presentation.schemas.vital_schema import (
    VitalCreateRequest,
    VitalListResponse,
    VitalResponse,
    VitalUpdateRequest,
)

router = APIRouter(prefix="/api/v1/vitals", tags=["vitals"])


@router.post(
    "",
    response_model=VitalResponse,
    status_code=201,
    summary="Record vital sign data",
    description="Records a single vital sign measurement for a patient. The patient must exist in the system.",
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Invalid or missing Bearer token",
            "content": {
                "application/json": {
                    "examples": {
                        "missing_token": {
                            "summary": "No token provided",
                            "value": {"detail": "Not authenticated"},
                        },
                        "invalid_token": {
                            "summary": "Invalid token",
                            "value": {"detail": "Invalid token"},
                        },
                    }
                }
            },
        },
        404: {
            "model": ErrorResponse,
            "description": "Patient not found",
        },
    },
)
async def create_vital(
    request: VitalCreateRequest,
    _: bool = Depends(verify_bearer_token),
    db: AsyncSession = Depends(get_db_session),
) -> VitalResponse:
    service = VitalService(db)
    return await service.create_vital(request)


@router.get(
    "/patient/{patient_id}",
    response_model=VitalListResponse,
    summary="Query vital records by time range",
    description="Retrieves vital records for a patient within specified time range. Optionally filter by vital type.",
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Invalid or missing Bearer token",
            "content": {
                "application/json": {
                    "examples": {
                        "missing_token": {
                            "summary": "No token provided",
                            "value": {"detail": "Not authenticated"},
                        },
                        "invalid_token": {
                            "summary": "Invalid token",
                            "value": {"detail": "Invalid token"},
                        },
                    }
                }
            },
        },
    },
)
async def get_vitals(
    patient_id: str = Path(
        ...,
        description="Hospital patient identifier",
        examples=["P00001234"],
    ),
    from_: datetime = Query(
        ...,
        alias="from",
        description="Start of time range, inclusive (ISO 8601 format)",
        examples=["2025-12-01T00:00:00Z"],
    ),
    to: datetime = Query(
        ...,
        description="End of time range, inclusive (ISO 8601 format)",
        examples=["2025-12-31T23:59:59Z"],
    ),
    vital_type: VitalType | None = Query(
        None,
        description="Optional filter by vital type (HR, RR, SBP, DBP, SpO2, BT)",
        examples=["HR"],
    ),
    _: bool = Depends(verify_bearer_token),
    db: AsyncSession = Depends(get_db_session),
) -> VitalListResponse:
    service = VitalService(db)
    return await service.get_vitals(patient_id, from_, to, vital_type)


@router.put(
    "/{vital_id}",
    response_model=VitalResponse,
    summary="Correct vital record",
    description="Updates a vital record value. Requires version field for optimistic locking.",
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Invalid or missing Bearer token",
            "content": {
                "application/json": {
                    "examples": {
                        "missing_token": {
                            "summary": "No token provided",
                            "value": {"detail": "Not authenticated"},
                        },
                        "invalid_token": {
                            "summary": "Invalid token",
                            "value": {"detail": "Invalid token"},
                        },
                    }
                }
            },
        },
        404: {
            "model": ErrorResponse,
            "description": "Vital record not found",
        },
        409: {
            "model": ErrorResponse,
            "description": "Version mismatch - record was modified by another request",
        },
    },
)
async def update_vital(
    request: VitalUpdateRequest,
    vital_id: UUID = Path(
        ...,
        description="Unique identifier of the vital record (UUID)",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    ),
    _: bool = Depends(verify_bearer_token),
    db: AsyncSession = Depends(get_db_session),
) -> VitalResponse:
    service = VitalService(db)
    return await service.update_vital(vital_id, request)

from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.patient_service import PatientService
from app.dependencies import verify_bearer_token
from app.infrastructure.database import get_db_session
from app.presentation.schemas.error_schema import ErrorResponse
from app.presentation.schemas.patient_schema import (
    PatientCreateRequest,
    PatientResponse,
    PatientUpdateRequest,
)

router = APIRouter(prefix="/api/v1/patients", tags=["patients"])


@router.post(
    "",
    response_model=PatientResponse,
    status_code=201,
    summary="Register a new patient",
    description="Creates a new patient record in the hospital system.",
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Invalid or missing Bearer token",
        },
        409: {
            "model": ErrorResponse,
            "description": "Patient with this patient_id already exists",
        },
    },
)
async def register_patient(
    request: PatientCreateRequest,
    _: bool = Depends(verify_bearer_token),
    db: AsyncSession = Depends(get_db_session),
) -> PatientResponse:
    service = PatientService(db)
    patient = await service.create_patient(request)
    await db.commit()
    return PatientResponse.model_validate(patient)


@router.put(
    "/{patient_id}",
    response_model=PatientResponse,
    summary="Update patient information",
    description="Updates an existing patient record. Requires version field for optimistic locking.",
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Invalid or missing Bearer token",
        },
        404: {
            "model": ErrorResponse,
            "description": "Patient not found",
        },
        409: {
            "model": ErrorResponse,
            "description": "Version mismatch - record was modified by another request",
        },
    },
)
async def update_patient(
    request: PatientUpdateRequest,
    patient_id: str = Path(
        ...,
        description="Hospital patient identifier",
        examples=["P00001234"],
    ),
    _: bool = Depends(verify_bearer_token),
    db: AsyncSession = Depends(get_db_session),
) -> PatientResponse:
    service = PatientService(db)
    patient = await service.update_patient(patient_id, request)
    await db.commit()
    return PatientResponse.model_validate(patient)

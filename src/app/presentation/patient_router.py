from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.patient_service import PatientService
from app.dependencies import verify_bearer_token
from app.infrastructure.database import get_db_session
from app.presentation.schemas.patient_schema import (
    PatientCreateRequest,
    PatientResponse,
    PatientUpdateRequest,
)

router = APIRouter(prefix="/api/v1/patients", tags=["patients"])


@router.post("", response_model=PatientResponse, status_code=201)
async def register_patient(
    request: PatientCreateRequest,
    _: bool = Depends(verify_bearer_token),
    db: AsyncSession = Depends(get_db_session),
) -> PatientResponse:
    service = PatientService(db)
    patient = await service.create_patient(request)
    await db.commit()
    return PatientResponse.model_validate(patient)


@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: str,
    request: PatientUpdateRequest,
    _: bool = Depends(verify_bearer_token),
    db: AsyncSession = Depends(get_db_session),
) -> PatientResponse:
    service = PatientService(db)
    patient = await service.update_patient(patient_id, request)
    await db.commit()
    return PatientResponse.model_validate(patient)

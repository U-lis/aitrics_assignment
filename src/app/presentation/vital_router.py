from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.vital_service import VitalService
from app.dependencies import verify_bearer_token
from app.domain.vital_type import VitalType
from app.infrastructure.database import get_db_session
from app.presentation.schemas.vital_schema import (
    VitalCreateRequest,
    VitalListResponse,
    VitalResponse,
    VitalUpdateRequest,
)

router = APIRouter(tags=["vitals"])


@router.post("/api/v1/vitals", response_model=VitalResponse, status_code=201)
async def create_vital(
    request: VitalCreateRequest,
    _: bool = Depends(verify_bearer_token),
    db: AsyncSession = Depends(get_db_session),
) -> VitalResponse:
    service = VitalService(db)
    return await service.create_vital(request)


@router.get("/api/v1/patients/{patient_id}/vitals", response_model=VitalListResponse)
async def get_vitals(
    patient_id: str,
    from_: datetime = Query(..., alias="from"),
    to: datetime = Query(...),
    vital_type: VitalType | None = None,
    _: bool = Depends(verify_bearer_token),
    db: AsyncSession = Depends(get_db_session),
) -> VitalListResponse:
    service = VitalService(db)
    return await service.get_vitals(patient_id, from_, to, vital_type)


@router.put("/api/v1/vitals/{vital_id}", response_model=VitalResponse)
async def update_vital(
    vital_id: UUID,
    request: VitalUpdateRequest,
    _: bool = Depends(verify_bearer_token),
    db: AsyncSession = Depends(get_db_session),
) -> VitalResponse:
    service = VitalService(db)
    return await service.update_vital(vital_id, request)

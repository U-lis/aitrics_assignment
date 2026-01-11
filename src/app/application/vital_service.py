from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exceptions import OptimisticLockError, PatientNotFoundError, VitalNotFoundError
from app.domain.vital_type import VitalType
from app.infrastructure.models.vital_model import VitalModel
from app.infrastructure.repositories.patient_repository import PatientRepository
from app.infrastructure.repositories.vital_repository import VitalRepository
from app.presentation.schemas.vital_schema import (
    VitalCreateRequest,
    VitalItem,
    VitalListResponse,
    VitalResponse,
    VitalUpdateRequest,
)


class VitalService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.vital_repo = VitalRepository(session)
        self.patient_repo = PatientRepository(session)

    async def create_vital(self, request: VitalCreateRequest) -> VitalResponse:
        if not await self.patient_repo.exists(request.patient_id):
            raise PatientNotFoundError(f"Patient {request.patient_id} not found")

        vital = VitalModel(
            patient_id=request.patient_id,
            recorded_at=request.recorded_at,
            vital_type=request.vital_type.value,
            value=Decimal(str(request.value)),
        )
        saved = await self.vital_repo.save(vital)
        return VitalResponse.model_validate(saved)

    async def get_vitals(
        self,
        patient_id: str,
        from_: datetime,
        to: datetime,
        vital_type: VitalType | None = None,
    ) -> VitalListResponse:
        vitals = await self.vital_repo.find_by_time_range(
            patient_id=patient_id,
            start_time=from_,
            end_time=to,
            vital_type=vital_type,
        )
        items = [VitalItem(recorded_at=v.recorded_at, value=float(v.value)) for v in vitals]
        return VitalListResponse(
            patient_id=patient_id,
            vital_type=vital_type.value if vital_type else None,
            items=items,
        )

    async def update_vital(
        self,
        vital_id: UUID,
        request: VitalUpdateRequest,
    ) -> VitalResponse:
        try:
            updated = await self.vital_repo.update_with_version(
                vital_id=vital_id,
                expected_version=request.version,
                value=Decimal(str(request.value)),
                vital_type=request.vital_type.value,
            )
            return VitalResponse.model_validate(updated)
        except OptimisticLockError:
            existing = await self.vital_repo.find_by_id(vital_id)
            if existing is None:
                raise VitalNotFoundError(f"Vital {vital_id} not found") from None
            raise

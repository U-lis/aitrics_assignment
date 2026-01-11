from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exceptions import (
    DuplicatePatientIdError,
    OptimisticLockError,
    PatientNotFoundError,
)
from app.infrastructure.models.patient_model import PatientModel
from app.infrastructure.repositories.patient_repository import PatientRepository
from app.presentation.schemas.patient_schema import (
    PatientCreateRequest,
    PatientUpdateRequest,
)


class PatientService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = PatientRepository(session)

    async def create_patient(self, dto: PatientCreateRequest) -> PatientModel:
        if await self.repository.exists(dto.patient_id):
            raise DuplicatePatientIdError(f"Patient {dto.patient_id} already exists")

        patient = PatientModel(
            patient_id=dto.patient_id,
            name=dto.name,
            gender=dto.gender,
            birth_date=dto.birth_date,
        )
        return await self.repository.save(patient)

    async def update_patient(self, patient_id: str, dto: PatientUpdateRequest) -> PatientModel:
        existing = await self.repository.find_by_patient_id(patient_id)
        if existing is None:
            raise PatientNotFoundError(f"Patient {patient_id} not found")

        try:
            return await self.repository.update_with_version(
                patient_id=patient_id,
                expected_version=dto.version,
                name=dto.name,
                gender=dto.gender,
                birth_date=dto.birth_date,
            )
        except OptimisticLockError:
            raise OptimisticLockError(f"Version mismatch: expected {dto.version}, current {existing.version}") from None

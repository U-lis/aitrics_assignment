from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exceptions import OptimisticLockError
from app.infrastructure.models.patient_model import PatientModel


class PatientRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_id(self, id: UUID) -> PatientModel | None:
        stmt = select(PatientModel).where(PatientModel.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_patient_id(self, patient_id: str) -> PatientModel | None:
        stmt = select(PatientModel).where(PatientModel.patient_id == patient_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def exists(self, patient_id: str) -> bool:
        patient = await self.find_by_patient_id(patient_id)
        return patient is not None

    async def save(self, patient: PatientModel) -> PatientModel:
        self.session.add(patient)
        await self.session.flush()
        await self.session.refresh(patient)
        return patient

    async def update_with_version(
        self,
        patient_id: str,
        expected_version: int,
        **values,
    ) -> PatientModel:
        stmt = (
            update(PatientModel)
            .where(
                PatientModel.patient_id == patient_id,
                PatientModel.version == expected_version,
            )
            .values(**values, version=PatientModel.version + 1)
            .returning(PatientModel)
        )
        result = await self.session.execute(stmt)
        updated = result.scalar_one_or_none()
        if updated is None:
            raise OptimisticLockError(f"Version mismatch for patient {patient_id}")
        return updated

    async def delete(self, patient_id: str) -> bool:
        patient = await self.find_by_patient_id(patient_id)
        if patient is None:
            return False
        await self.session.delete(patient)
        await self.session.flush()
        return True

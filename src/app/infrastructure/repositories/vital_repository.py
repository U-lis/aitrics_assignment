from datetime import datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exceptions import OptimisticLockError
from app.domain.vital_type import VitalType
from app.infrastructure.models.vital_model import VitalModel


class VitalRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_id(self, id: UUID) -> VitalModel | None:
        stmt = select(VitalModel).where(VitalModel.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    # async def find_by_patient_id(self, patient_id: str) -> list[VitalModel]:
    #     stmt = select(VitalModel).where(VitalModel.patient_id == patient_id)
    #     result = await self.session.execute(stmt)
    #     return list(result.scalars().all())

    async def find_by_time_range(
        self,
        patient_id: str,
        start_time: datetime,
        end_time: datetime,
        vital_type: VitalType | None = None,
    ) -> list[VitalModel]:
        stmt = select(VitalModel).where(
            VitalModel.patient_id == patient_id,
            VitalModel.recorded_at >= start_time,
            VitalModel.recorded_at <= end_time,
        )
        if vital_type is not None:
            stmt = stmt.where(VitalModel.vital_type == vital_type.value)
        stmt = stmt.order_by(VitalModel.recorded_at)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def save(self, vital: VitalModel) -> VitalModel:
        self.session.add(vital)
        await self.session.flush()
        await self.session.refresh(vital)
        return vital

    async def update_with_version(
        self,
        vital_id: UUID,
        expected_version: int,
        **values,
    ) -> VitalModel:
        stmt = (
            update(VitalModel)
            .where(
                VitalModel.id == vital_id,
                VitalModel.version == expected_version,
            )
            .values(**values, version=VitalModel.version + 1)
            .returning(VitalModel)
        )
        result = await self.session.execute(stmt)
        updated = result.scalar_one_or_none()
        if updated is None:
            raise OptimisticLockError(f"Version mismatch for vital {vital_id}")
        return updated

    # async def delete(self, vital_id: UUID) -> bool:
    #     vital = await self.find_by_id(vital_id)
    #     if vital is None:
    #         return False
    #     await self.session.delete(vital)
    #     await self.session.flush()
    #     return True

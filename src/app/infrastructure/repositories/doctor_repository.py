from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.models.doctor_model import DoctorModel


class DoctorRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_id(self, doctor_id: str) -> DoctorModel | None:
        stmt = select(DoctorModel).where(DoctorModel.id == doctor_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def save(self, doctor: DoctorModel) -> DoctorModel:
        self.session.add(doctor)
        await self.session.flush()
        await self.session.refresh(doctor)
        return doctor

    async def update_tokens(
        self,
        doctor_id: str,
        access_token: str,
        refresh_token: str,
        expires_at: datetime,
    ) -> DoctorModel | None:
        doctor = await self.find_by_id(doctor_id)
        if doctor is None:
            return None
        doctor.set_tokens(access_token, refresh_token, expires_at)
        await self.session.flush()
        await self.session.refresh(doctor)
        return doctor

    async def clear_tokens(self, doctor_id: str) -> bool:
        doctor = await self.find_by_id(doctor_id)
        if doctor is None:
            return False
        doctor.access_token = None
        doctor.refresh_token = None
        doctor.access_token_expires_at = None
        await self.session.flush()
        return True

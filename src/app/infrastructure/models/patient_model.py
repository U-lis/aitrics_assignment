import uuid

from sqlalchemy import CheckConstraint, Date, Index, String, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.models.base import Base, TimestampMixin


class PatientModel(Base, TimestampMixin):
    __tablename__ = "patients"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    patient_id: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    gender: Mapped[str] = mapped_column(String(1), nullable=False)
    birth_date: Mapped[str] = mapped_column(Date, nullable=False)
    version: Mapped[int] = mapped_column(default=1, server_default=text("1"), nullable=False)

    __table_args__ = (
        CheckConstraint("gender IN ('M', 'F')", name="ck_patients_gender"),
        Index("ix_patients_patient_id", "patient_id"),
    )

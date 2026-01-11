import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Numeric, String, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.vital_type import VitalType
from app.infrastructure.models.base import Base, TimestampMixin


class VitalModel(Base, TimestampMixin):
    __tablename__ = "vitals"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    patient_id: Mapped[str] = mapped_column(
        String(20),
        ForeignKey("patients.patient_id", ondelete="CASCADE"),
        nullable=False,
    )
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    vital_type: Mapped[str] = mapped_column(String(10), nullable=False)
    value: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    version: Mapped[int] = mapped_column(default=1, server_default=text("1"), nullable=False)

    __table_args__ = (
        CheckConstraint(
            f"vital_type IN ('{VitalType.HR}', '{VitalType.RR}', '{VitalType.SBP}', "
            f"'{VitalType.DBP}', '{VitalType.SPO2}', '{VitalType.BT}')",
            name="ck_vitals_vital_type",
        ),
        Index("ix_vitals_patient_id", "patient_id"),
        Index("ix_vitals_recorded_at", "recorded_at"),
    )

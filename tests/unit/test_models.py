from datetime import UTC, date, datetime
from decimal import Decimal

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.domain.vital_type import VitalType
from app.infrastructure.models.patient_model import PatientModel
from app.infrastructure.models.vital_model import VitalModel


@pytest.mark.asyncio
async def test_patient_model_create(db_session):
    """Create Patient (version=1)."""
    patient = PatientModel(
        patient_id="P001",
        name="Patient Kim",
        gender="M",
        birth_date=date(1990, 1, 15),
    )
    db_session.add(patient)
    await db_session.flush()

    result = await db_session.execute(select(PatientModel).where(PatientModel.patient_id == "P001"))
    found = result.scalar_one()

    assert found.patient_id == "P001"
    assert found.version == 1


@pytest.mark.asyncio
async def test_patient_model_auto_timestamps(db_session):
    """created_at, updated_at auto-generated."""
    patient = PatientModel(
        patient_id="P002",
        name="Patient Lee",
        gender="F",
        birth_date=date(1985, 5, 20),
    )
    db_session.add(patient)
    await db_session.flush()
    await db_session.refresh(patient)

    assert patient.created_at is not None
    assert patient.updated_at is not None


@pytest.mark.asyncio
async def test_vital_model_create(db_session):
    """Create Vital with FK."""
    patient = PatientModel(
        patient_id="P003",
        name="Patient Park",
        gender="M",
        birth_date=date(1975, 3, 10),
    )
    db_session.add(patient)
    await db_session.flush()

    vital = VitalModel(
        patient_id="P003",
        recorded_at=datetime.now(UTC),
        vital_type=VitalType.HR.value,
        value=Decimal("72.5"),
    )
    db_session.add(vital)
    await db_session.flush()

    result = await db_session.execute(select(VitalModel).where(VitalModel.patient_id == "P003"))
    found = result.scalar_one()

    assert found.vital_type == "HR"
    assert found.value == Decimal("72.5")


@pytest.mark.asyncio
async def test_vital_model_patient_fk_constraint(db_session):
    """FK violation raises error."""
    vital = VitalModel(
        patient_id="NONEXISTENT",
        recorded_at=datetime.now(UTC),
        vital_type=VitalType.HR.value,
        value=Decimal("72.5"),
    )
    db_session.add(vital)

    with pytest.raises(IntegrityError):
        await db_session.flush()

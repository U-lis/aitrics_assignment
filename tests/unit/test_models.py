from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.domain.vital_type import VitalType
from app.infrastructure.auth.password_handler import hash_password
from app.infrastructure.models.doctor_model import DoctorModel
from app.infrastructure.models.patient_model import PatientModel
from app.infrastructure.models.vital_model import VitalModel


@pytest.mark.asyncio
async def test_doctor_model_create(db_session):
    """Create and query Doctor."""
    doctor = DoctorModel(
        id="doctor001",
        password_hash=hash_password("password123"),
        name="Dr. Kim",
    )
    db_session.add(doctor)
    await db_session.flush()

    result = await db_session.execute(select(DoctorModel).where(DoctorModel.id == "doctor001"))
    found = result.scalar_one()

    assert found.id == "doctor001"
    assert found.name == "Dr. Kim"


@pytest.mark.asyncio
async def test_doctor_model_set_tokens(db_session):
    """set_tokens() stores encrypted tokens."""
    doctor = DoctorModel(
        id="doctor002",
        password_hash=hash_password("password123"),
        name="Dr. Lee",
    )
    db_session.add(doctor)
    await db_session.flush()

    expires_at = datetime.now(UTC) + timedelta(hours=1)
    doctor.set_tokens("access_token_value", "refresh_token_value", expires_at)
    await db_session.flush()

    assert doctor.access_token is not None
    assert doctor.access_token != "access_token_value"  # Should be encrypted
    assert doctor.refresh_token is not None
    assert doctor.refresh_token != "refresh_token_value"


@pytest.mark.asyncio
async def test_doctor_model_decrypted_properties(db_session):
    """decrypted_access_token, decrypted_refresh_token work."""
    doctor = DoctorModel(
        id="doctor003",
        password_hash=hash_password("password123"),
        name="Dr. Park",
    )
    db_session.add(doctor)
    await db_session.flush()

    expires_at = datetime.now(UTC) + timedelta(hours=1)
    doctor.set_tokens("my_access_token", "my_refresh_token", expires_at)
    await db_session.flush()

    assert doctor.decrypted_access_token == "my_access_token"
    assert doctor.decrypted_refresh_token == "my_refresh_token"


@pytest.mark.asyncio
async def test_doctor_model_is_access_token_valid_true(db_session):
    """Valid within expires_at."""
    doctor = DoctorModel(
        id="doctor004",
        password_hash=hash_password("password123"),
        name="Dr. Choi",
    )
    db_session.add(doctor)
    await db_session.flush()

    expires_at = datetime.now(UTC) + timedelta(hours=1)
    doctor.set_tokens("token", "refresh", expires_at)
    await db_session.flush()

    assert doctor.is_access_token_valid() is True


@pytest.mark.asyncio
async def test_doctor_model_is_access_token_valid_false(db_session):
    """Invalid after expires_at."""
    doctor = DoctorModel(
        id="doctor005",
        password_hash=hash_password("password123"),
        name="Dr. Jung",
    )
    db_session.add(doctor)
    await db_session.flush()

    expires_at = datetime.now(UTC) - timedelta(hours=1)
    doctor.set_tokens("token", "refresh", expires_at)
    await db_session.flush()

    assert doctor.is_access_token_valid() is False


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

from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest

from app.domain.exceptions import OptimisticLockError
from app.domain.vital_type import VitalType
from app.infrastructure.models.patient_model import PatientModel
from app.infrastructure.models.vital_model import VitalModel
from app.infrastructure.repositories.patient_repository import PatientRepository
from app.infrastructure.repositories.vital_repository import VitalRepository


@pytest.mark.asyncio
async def test_patient_repo_find_by_patient_id(db_session):
    """Find Patient by patient_id."""
    patient = PatientModel(
        patient_id="REPO_P001",
        name="Repo Patient",
        gender="M",
        birth_date=date(1990, 1, 1),
    )
    db_session.add(patient)
    await db_session.flush()

    repo = PatientRepository(db_session)
    found = await repo.find_by_patient_id("REPO_P001")

    assert found is not None
    assert found.name == "Repo Patient"


@pytest.mark.asyncio
async def test_patient_repo_exists(db_session):
    """Check patient_id exists."""
    patient = PatientModel(
        patient_id="REPO_P002",
        name="Exist Patient",
        gender="F",
        birth_date=date(1985, 6, 15),
    )
    db_session.add(patient)
    await db_session.flush()

    repo = PatientRepository(db_session)

    assert await repo.exists("REPO_P002") is True
    assert await repo.exists("NONEXISTENT") is False


@pytest.mark.asyncio
async def test_vital_repo_find_by_time_range(db_session):
    """Query by time range."""
    patient = PatientModel(
        patient_id="REPO_P003",
        name="Range Patient",
        gender="M",
        birth_date=date(1970, 1, 1),
    )
    db_session.add(patient)
    await db_session.flush()

    now = datetime.now(UTC)
    vitals = [
        VitalModel(
            patient_id="REPO_P003",
            recorded_at=now - timedelta(hours=2),
            vital_type=VitalType.HR.value,
            value=Decimal("70"),
        ),
        VitalModel(
            patient_id="REPO_P003",
            recorded_at=now - timedelta(hours=1),
            vital_type=VitalType.RR.value,
            value=Decimal("16"),
        ),
        VitalModel(
            patient_id="REPO_P003",
            recorded_at=now,
            vital_type=VitalType.HR.value,
            value=Decimal("75"),
        ),
    ]
    for v in vitals:
        db_session.add(v)
    await db_session.flush()

    repo = VitalRepository(db_session)

    # Query all in range
    results = await repo.find_by_time_range(
        "REPO_P003",
        now - timedelta(hours=3),
        now + timedelta(minutes=1),
    )
    assert len(results) == 3


@pytest.mark.asyncio
async def test_vital_repo_find_by_time_range_with_type(db_session):
    """Filter by vital_type."""
    patient = PatientModel(
        patient_id="REPO_P004",
        name="Type Patient",
        gender="F",
        birth_date=date(1980, 5, 5),
    )
    db_session.add(patient)
    await db_session.flush()

    now = datetime.now(UTC)
    vitals = [
        VitalModel(
            patient_id="REPO_P004",
            recorded_at=now - timedelta(hours=1),
            vital_type=VitalType.HR.value,
            value=Decimal("70"),
        ),
        VitalModel(
            patient_id="REPO_P004",
            recorded_at=now,
            vital_type=VitalType.RR.value,
            value=Decimal("18"),
        ),
    ]
    for v in vitals:
        db_session.add(v)
    await db_session.flush()

    repo = VitalRepository(db_session)

    # Filter by HR only
    results = await repo.find_by_time_range(
        "REPO_P004",
        now - timedelta(hours=2),
        now + timedelta(minutes=1),
        vital_type=VitalType.HR,
    )
    assert len(results) == 1
    assert results[0].vital_type == VitalType.HR.value


@pytest.mark.asyncio
async def test_patient_repo_update_with_version_success(db_session):
    """Optimistic lock update succeeds with correct version."""
    patient = PatientModel(
        patient_id="LOCK_P001",
        name="Original Name",
        gender="M",
        birth_date=date(1990, 1, 1),
    )
    db_session.add(patient)
    await db_session.flush()

    repo = PatientRepository(db_session)
    updated = await repo.update_with_version(
        patient_id="LOCK_P001",
        expected_version=1,
        name="Updated Name",
        gender="F",
    )

    assert updated.name == "Updated Name"
    assert updated.gender == "F"
    assert updated.version == 2


@pytest.mark.asyncio
async def test_patient_repo_update_with_version_conflict(db_session):
    """Optimistic lock update fails with wrong version."""
    patient = PatientModel(
        patient_id="LOCK_P002",
        name="Original",
        gender="M",
        birth_date=date(1990, 1, 1),
    )
    db_session.add(patient)
    await db_session.flush()

    repo = PatientRepository(db_session)

    # First update succeeds (version 1 -> 2)
    await repo.update_with_version(
        patient_id="LOCK_P002",
        expected_version=1,
        name="First Update",
    )

    # Second update with stale version (1) should fail
    with pytest.raises(OptimisticLockError) as exc_info:
        await repo.update_with_version(
            patient_id="LOCK_P002",
            expected_version=1,  # Stale version
            name="Second Update",
        )

    assert "Version mismatch" in str(exc_info.value)

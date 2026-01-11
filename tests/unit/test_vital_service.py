from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.vital_service import VitalService
from app.domain.exceptions import OptimisticLockError, PatientNotFoundError, VitalNotFoundError
from app.domain.vital_type import VitalType
from app.infrastructure.models.patient_model import PatientModel
from app.infrastructure.models.vital_model import VitalModel
from app.presentation.schemas.vital_schema import VitalCreateRequest, VitalUpdateRequest


async def create_patient(db_session: AsyncSession, patient_id: str) -> PatientModel:
    """Helper to create a patient."""
    patient = PatientModel(
        patient_id=patient_id,
        name="Test Patient",
        gender="M",
        birth_date=date(1990, 1, 1),
    )
    db_session.add(patient)
    await db_session.flush()
    return patient


async def create_vital(
    db_session: AsyncSession,
    patient_id: str,
    recorded_at: datetime,
    vital_type: str = "HR",
    value: float = 72.0,
) -> VitalModel:
    """Helper to create a vital."""
    vital = VitalModel(
        patient_id=patient_id,
        recorded_at=recorded_at,
        vital_type=vital_type,
        value=Decimal(str(value)),
    )
    db_session.add(vital)
    await db_session.flush()
    await db_session.refresh(vital)
    return vital


@pytest.mark.asyncio
async def test_create_vital_success(db_session: AsyncSession):
    """Test creating a vital for existing patient."""
    patient_id = f"SVC_{uuid4().hex[:8]}"
    await create_patient(db_session, patient_id)

    service = VitalService(db_session)
    request = VitalCreateRequest(
        patient_id=patient_id,
        recorded_at=datetime(2024, 1, 1, 10, 0, 0, tzinfo=UTC),
        vital_type=VitalType.HR,
        value=72.5,
    )

    response = await service.create_vital(request)

    assert response.patient_id == patient_id
    assert response.vital_type == "HR"
    assert response.value == 72.5
    assert response.version == 1


@pytest.mark.asyncio
async def test_create_vital_patient_not_found(db_session: AsyncSession):
    """Test creating a vital for non-existing patient raises error."""
    service = VitalService(db_session)
    request = VitalCreateRequest(
        patient_id="NONEXISTENT",
        recorded_at=datetime(2024, 1, 1, 10, 0, 0, tzinfo=UTC),
        vital_type=VitalType.HR,
        value=72.5,
    )

    with pytest.raises(PatientNotFoundError):
        await service.create_vital(request)


@pytest.mark.asyncio
async def test_get_vitals_with_items(db_session: AsyncSession):
    """Test getting vitals returns items."""
    patient_id = f"SVC_{uuid4().hex[:8]}"
    await create_patient(db_session, patient_id)
    await create_vital(
        db_session,
        patient_id,
        datetime(2024, 1, 1, 10, 0, 0, tzinfo=UTC),
        value=72.0,
    )

    service = VitalService(db_session)
    response = await service.get_vitals(
        patient_id=patient_id,
        from_=datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC),
        to=datetime(2024, 1, 1, 23, 59, 59, tzinfo=UTC),
    )

    assert response.patient_id == patient_id
    assert len(response.items) == 1
    assert response.items[0].value == 72.0


@pytest.mark.asyncio
async def test_get_vitals_with_type_filter(db_session: AsyncSession):
    """Test getting vitals with type filter."""
    patient_id = f"SVC_{uuid4().hex[:8]}"
    await create_patient(db_session, patient_id)
    await create_vital(db_session, patient_id, datetime(2024, 1, 1, 10, 0, 0, tzinfo=UTC), "HR")
    await create_vital(db_session, patient_id, datetime(2024, 1, 1, 11, 0, 0, tzinfo=UTC), "RR")

    service = VitalService(db_session)
    response = await service.get_vitals(
        patient_id=patient_id,
        from_=datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC),
        to=datetime(2024, 1, 1, 23, 59, 59, tzinfo=UTC),
        vital_type=VitalType.HR,
    )

    assert len(response.items) == 1
    assert response.vital_type == "HR"


@pytest.mark.asyncio
async def test_update_vital_success(db_session: AsyncSession):
    """Test updating a vital."""
    patient_id = f"SVC_{uuid4().hex[:8]}"
    await create_patient(db_session, patient_id)
    vital = await create_vital(
        db_session,
        patient_id,
        datetime(2024, 1, 1, 10, 0, 0, tzinfo=UTC),
    )

    service = VitalService(db_session)
    request = VitalUpdateRequest(
        value=80.0,
        vital_type=VitalType.HR,
        version=1,
    )

    response = await service.update_vital(vital.id, request)

    assert response.value == 80.0
    assert response.version == 2


@pytest.mark.asyncio
async def test_update_vital_not_found(db_session: AsyncSession):
    """Test updating non-existing vital raises error."""
    service = VitalService(db_session)
    request = VitalUpdateRequest(
        value=80.0,
        vital_type=VitalType.HR,
        version=1,
    )

    with pytest.raises(VitalNotFoundError):
        await service.update_vital(uuid4(), request)


@pytest.mark.asyncio
async def test_update_vital_version_mismatch(db_session: AsyncSession):
    """Test updating with wrong version raises OptimisticLockError."""
    patient_id = f"SVC_{uuid4().hex[:8]}"
    await create_patient(db_session, patient_id)
    vital = await create_vital(
        db_session,
        patient_id,
        datetime(2024, 1, 1, 10, 0, 0, tzinfo=UTC),
    )

    service = VitalService(db_session)

    # First update succeeds
    request1 = VitalUpdateRequest(value=80.0, vital_type=VitalType.HR, version=1)
    await service.update_vital(vital.id, request1)

    # Second update with stale version fails
    request2 = VitalUpdateRequest(value=85.0, vital_type=VitalType.HR, version=1)
    with pytest.raises(OptimisticLockError):
        await service.update_vital(vital.id, request2)

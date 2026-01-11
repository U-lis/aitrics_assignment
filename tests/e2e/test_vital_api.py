from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.models.patient_model import PatientModel
from app.infrastructure.models.vital_model import VitalModel

BEARER_TOKEN = "test-bearer-token"
AUTH_HEADERS = {"Authorization": f"Bearer {BEARER_TOKEN}"}


async def create_test_patient(db_session: AsyncSession, patient_id: str) -> PatientModel:
    """Helper to create a patient directly in DB."""
    patient = PatientModel(
        patient_id=patient_id,
        name="Test Patient",
        gender="M",
        birth_date=date(1990, 1, 1),
    )
    db_session.add(patient)
    await db_session.flush()
    await db_session.refresh(patient)
    return patient


async def create_test_vital(
    db_session: AsyncSession,
    patient_id: str,
    recorded_at: datetime,
    vital_type: str = "HR",
    value: float = 72.0,
) -> VitalModel:
    """Helper to create a vital directly in DB."""
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


class TestCreateVital:
    @pytest.mark.asyncio
    async def test_create_vital_success(self, test_client: AsyncClient, db_session: AsyncSession):
        patient_id = f"CREATE_{uuid4().hex[:8]}"
        await create_test_patient(db_session, patient_id)
        await db_session.commit()

        response = await test_client.post(
            "/api/v1/vitals",
            headers=AUTH_HEADERS,
            json={
                "patient_id": patient_id,
                "recorded_at": "2024-01-01T10:00:00Z",
                "vital_type": "HR",
                "value": 72.5,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["patient_id"] == patient_id
        assert data["vital_type"] == "HR"
        assert data["value"] == 72.5
        assert data["version"] == 1
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    @pytest.mark.asyncio
    async def test_create_vital_invalid_patient(self, test_client: AsyncClient):
        response = await test_client.post(
            "/api/v1/vitals",
            headers=AUTH_HEADERS,
            json={
                "patient_id": "UNKNOWN_PATIENT",
                "recorded_at": "2024-01-01T10:00:00Z",
                "vital_type": "HR",
                "value": 72.0,
            },
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_create_vital_invalid_type(self, test_client: AsyncClient, db_session: AsyncSession):
        patient_id = f"INVALID_{uuid4().hex[:8]}"
        await create_test_patient(db_session, patient_id)
        await db_session.commit()

        response = await test_client.post(
            "/api/v1/vitals",
            headers=AUTH_HEADERS,
            json={
                "patient_id": patient_id,
                "recorded_at": "2024-01-01T10:00:00Z",
                "vital_type": "INVALID_TYPE",
                "value": 72.0,
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_vital_unauthorized(self, test_client: AsyncClient):
        response = await test_client.post(
            "/api/v1/vitals",
            json={
                "patient_id": "P001",
                "recorded_at": "2024-01-01T10:00:00Z",
                "vital_type": "HR",
                "value": 72.0,
            },
        )
        assert response.status_code == 401


class TestGetVitals:
    @pytest.mark.asyncio
    async def test_get_vitals_success(self, test_client: AsyncClient, db_session: AsyncSession):
        patient_id = f"GET_{uuid4().hex[:8]}"
        await create_test_patient(db_session, patient_id)
        await create_test_vital(
            db_session,
            patient_id,
            datetime(2024, 1, 1, 10, 0, 0, tzinfo=UTC),
        )
        await db_session.commit()

        response = await test_client.get(
            f"/api/v1/vitals/patient/{patient_id}",
            headers=AUTH_HEADERS,
            params={
                "from": "2024-01-01T00:00:00Z",
                "to": "2024-01-01T23:59:59Z",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["patient_id"] == patient_id
        assert len(data["items"]) == 1
        assert data["items"][0]["value"] == 72.0

    @pytest.mark.asyncio
    async def test_get_vitals_time_range(self, test_client: AsyncClient, db_session: AsyncSession):
        patient_id = f"RANGE_{uuid4().hex[:8]}"
        await create_test_patient(db_session, patient_id)

        for hour in [8, 10, 12, 14]:
            await create_test_vital(
                db_session,
                patient_id,
                datetime(2024, 1, 1, hour, 0, 0, tzinfo=UTC),
                value=70.0 + hour,
            )
        await db_session.commit()

        response = await test_client.get(
            f"/api/v1/vitals/patient/{patient_id}",
            headers=AUTH_HEADERS,
            params={
                "from": "2024-01-01T09:00:00Z",
                "to": "2024-01-01T13:00:00Z",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2

    @pytest.mark.asyncio
    async def test_get_vitals_type_filter(self, test_client: AsyncClient, db_session: AsyncSession):
        patient_id = f"FILTER_{uuid4().hex[:8]}"
        await create_test_patient(db_session, patient_id)

        for vtype in ["HR", "RR", "SpO2"]:
            await create_test_vital(
                db_session,
                patient_id,
                datetime(2024, 1, 1, 10, 0, 0, tzinfo=UTC),
                vital_type=vtype,
            )
        await db_session.commit()

        response = await test_client.get(
            f"/api/v1/vitals/patient/{patient_id}",
            headers=AUTH_HEADERS,
            params={
                "from": "2024-01-01T00:00:00Z",
                "to": "2024-01-01T23:59:59Z",
                "vital_type": "HR",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["vital_type"] == "HR"

    @pytest.mark.asyncio
    async def test_get_vitals_empty(self, test_client: AsyncClient, db_session: AsyncSession):
        patient_id = f"EMPTY_{uuid4().hex[:8]}"
        await create_test_patient(db_session, patient_id)
        await db_session.commit()

        response = await test_client.get(
            f"/api/v1/vitals/patient/{patient_id}",
            headers=AUTH_HEADERS,
            params={
                "from": "2024-01-01T00:00:00Z",
                "to": "2024-01-01T23:59:59Z",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []

    @pytest.mark.asyncio
    async def test_get_vitals_unauthorized(self, test_client: AsyncClient):
        response = await test_client.get(
            "/api/v1/vitals/patient/P001",
            params={
                "from": "2024-01-01T00:00:00Z",
                "to": "2024-01-01T23:59:59Z",
            },
        )
        assert response.status_code == 401


class TestUpdateVital:
    @pytest.mark.asyncio
    async def test_update_vital_success(self, test_client: AsyncClient, db_session: AsyncSession):
        patient_id = f"UPDATE_{uuid4().hex[:8]}"
        await create_test_patient(db_session, patient_id)
        vital = await create_test_vital(
            db_session,
            patient_id,
            datetime(2024, 1, 1, 10, 0, 0, tzinfo=UTC),
        )
        await db_session.commit()

        response = await test_client.put(
            f"/api/v1/vitals/{vital.id}",
            headers=AUTH_HEADERS,
            json={
                "value": 80.0,
                "vital_type": "HR",
                "version": 1,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["value"] == 80.0
        assert data["version"] == 2

    @pytest.mark.asyncio
    async def test_update_vital_change_type(self, test_client: AsyncClient, db_session: AsyncSession):
        patient_id = f"CHTYPE_{uuid4().hex[:8]}"
        await create_test_patient(db_session, patient_id)
        vital = await create_test_vital(
            db_session,
            patient_id,
            datetime(2024, 1, 1, 10, 0, 0, tzinfo=UTC),
        )
        await db_session.commit()

        response = await test_client.put(
            f"/api/v1/vitals/{vital.id}",
            headers=AUTH_HEADERS,
            json={
                "value": 98.6,
                "vital_type": "BT",
                "version": 1,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["vital_type"] == "BT"
        assert data["value"] == 98.6

    @pytest.mark.asyncio
    async def test_update_vital_optimistic_lock_conflict(self, test_client: AsyncClient, db_session: AsyncSession):
        patient_id = f"LOCK_{uuid4().hex[:8]}"
        await create_test_patient(db_session, patient_id)
        vital = await create_test_vital(
            db_session,
            patient_id,
            datetime(2024, 1, 1, 10, 0, 0, tzinfo=UTC),
        )
        await db_session.commit()

        response1 = await test_client.put(
            f"/api/v1/vitals/{vital.id}",
            headers=AUTH_HEADERS,
            json={
                "value": 80.0,
                "vital_type": "HR",
                "version": 1,
            },
        )
        assert response1.status_code == 200

        response2 = await test_client.put(
            f"/api/v1/vitals/{vital.id}",
            headers=AUTH_HEADERS,
            json={
                "value": 85.0,
                "vital_type": "HR",
                "version": 1,
            },
        )
        assert response2.status_code == 409
        assert "version" in response2.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_update_vital_not_found(self, test_client: AsyncClient):
        unknown_id = uuid4()
        response = await test_client.put(
            f"/api/v1/vitals/{unknown_id}",
            headers=AUTH_HEADERS,
            json={
                "value": 80.0,
                "vital_type": "HR",
                "version": 1,
            },
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

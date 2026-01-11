from httpx import AsyncClient

VALID_TOKEN = "test-bearer-token"
AUTH_HEADER = {"Authorization": f"Bearer {VALID_TOKEN}"}


class TestCreatePatient:
    async def test_create_patient_success(self, test_client: AsyncClient):
        response = await test_client.post(
            "/api/v1/patients",
            json={
                "patient_id": "P00001234",
                "name": "John Doe",
                "gender": "M",
                "birth_date": "1990-01-15",
            },
            headers=AUTH_HEADER,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["patient_id"] == "P00001234"
        assert data["name"] == "John Doe"
        assert data["gender"] == "M"
        assert data["birth_date"] == "1990-01-15"
        assert data["version"] == 1
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    async def test_create_patient_duplicate(self, test_client: AsyncClient):
        patient_data = {
            "patient_id": "P00001111",
            "name": "Jane Doe",
            "gender": "F",
            "birth_date": "1985-05-20",
        }

        response1 = await test_client.post(
            "/api/v1/patients",
            json=patient_data,
            headers=AUTH_HEADER,
        )
        assert response1.status_code == 201

        response2 = await test_client.post(
            "/api/v1/patients",
            json=patient_data,
            headers=AUTH_HEADER,
        )
        assert response2.status_code == 409
        assert "already exists" in response2.json()["detail"]

    async def test_create_patient_unauthorized(self, test_client: AsyncClient):
        response = await test_client.post(
            "/api/v1/patients",
            json={
                "patient_id": "P00002222",
                "name": "Test Patient",
                "gender": "M",
                "birth_date": "2000-01-01",
            },
        )
        assert response.status_code == 401


class TestUpdatePatient:
    async def test_update_patient_success(self, test_client: AsyncClient):
        create_response = await test_client.post(
            "/api/v1/patients",
            json={
                "patient_id": "P00003333",
                "name": "Original Name",
                "gender": "M",
                "birth_date": "1990-01-01",
            },
            headers=AUTH_HEADER,
        )
        assert create_response.status_code == 201

        update_response = await test_client.put(
            "/api/v1/patients/P00003333",
            json={
                "name": "Updated Name",
                "gender": "F",
                "birth_date": "1991-02-02",
                "version": 1,
            },
            headers=AUTH_HEADER,
        )

        assert update_response.status_code == 200
        data = update_response.json()
        assert data["name"] == "Updated Name"
        assert data["gender"] == "F"
        assert data["birth_date"] == "1991-02-02"
        assert data["version"] == 2

    async def test_update_patient_version_increment(self, test_client: AsyncClient):
        await test_client.post(
            "/api/v1/patients",
            json={
                "patient_id": "P00004444",
                "name": "Version Test",
                "gender": "M",
                "birth_date": "1990-01-01",
            },
            headers=AUTH_HEADER,
        )

        response1 = await test_client.put(
            "/api/v1/patients/P00004444",
            json={
                "name": "Version 2",
                "gender": "M",
                "birth_date": "1990-01-01",
                "version": 1,
            },
            headers=AUTH_HEADER,
        )
        assert response1.status_code == 200
        assert response1.json()["version"] == 2

        response2 = await test_client.put(
            "/api/v1/patients/P00004444",
            json={
                "name": "Version 3",
                "gender": "M",
                "birth_date": "1990-01-01",
                "version": 2,
            },
            headers=AUTH_HEADER,
        )
        assert response2.status_code == 200
        assert response2.json()["version"] == 3

    async def test_update_patient_optimistic_lock_conflict(self, test_client: AsyncClient):
        await test_client.post(
            "/api/v1/patients",
            json={
                "patient_id": "P00005555",
                "name": "Lock Test",
                "gender": "M",
                "birth_date": "1990-01-01",
            },
            headers=AUTH_HEADER,
        )

        response1 = await test_client.put(
            "/api/v1/patients/P00005555",
            json={
                "name": "First Update",
                "gender": "M",
                "birth_date": "1990-01-01",
                "version": 1,
            },
            headers=AUTH_HEADER,
        )
        assert response1.status_code == 200

        response2 = await test_client.put(
            "/api/v1/patients/P00005555",
            json={
                "name": "Second Update",
                "gender": "M",
                "birth_date": "1990-01-01",
                "version": 1,  # Same version as first update - should fail
            },
            headers=AUTH_HEADER,
        )
        assert response2.status_code == 409
        assert "Version mismatch" in response2.json()["detail"]

    async def test_update_patient_not_found(self, test_client: AsyncClient):
        response = await test_client.put(
            "/api/v1/patients/P99999999",
            json={
                "name": "Not Found",
                "gender": "M",
                "birth_date": "1990-01-01",
                "version": 1,
            },
            headers=AUTH_HEADER,
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    async def test_update_patient_unauthorized(self, test_client: AsyncClient):
        response = await test_client.put(
            "/api/v1/patients/P00006666",
            json={
                "name": "Unauthorized",
                "gender": "M",
                "birth_date": "1990-01-01",
                "version": 1,
            },
        )
        assert response.status_code == 401

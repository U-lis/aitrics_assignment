import pytest
from httpx import AsyncClient


class TestInferenceAPI:
    @pytest.mark.asyncio
    async def test_vital_risk_success(self, test_client: AsyncClient):
        """POST /api/v1/inference/vital-risk -> 200."""
        response = await test_client.post(
            "/api/v1/inference/vital-risk",
            headers={"Authorization": "Bearer test-bearer-token"},
            json={
                "patient_id": "P001",
                "records": [
                    {
                        "recorded_at": "2024-01-01T00:00:00Z",
                        "vitals": {"HR": 130, "SBP": 85, "SpO2": 85},
                    }
                ],
            },
        )

        assert response.status_code == 200

        data = response.json()
        assert data["patient_id"] == "P001"
        assert data["risk_score"] == 0.9
        assert data["risk_level"] == "HIGH"
        assert len(data["checked_rules"]) == 3
        assert "evaluated_at" in data

    @pytest.mark.asyncio
    async def test_vital_risk_unauthorized(self, test_client: AsyncClient):
        """No token -> 401."""
        response = await test_client.post(
            "/api/v1/inference/vital-risk",
            json={
                "patient_id": "P001",
                "records": [
                    {
                        "recorded_at": "2024-01-01T00:00:00Z",
                        "vitals": {"HR": 80, "SBP": 120, "SpO2": 98},
                    }
                ],
            },
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_vital_risk_invalid_token(self, test_client: AsyncClient):
        """Invalid token -> 401."""
        response = await test_client.post(
            "/api/v1/inference/vital-risk",
            headers={"Authorization": "Bearer wrong-token"},
            json={
                "patient_id": "P001",
                "records": [
                    {
                        "recorded_at": "2024-01-01T00:00:00Z",
                        "vitals": {"HR": 80, "SBP": 120, "SpO2": 98},
                    }
                ],
            },
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_vital_risk_empty_records(self, test_client: AsyncClient):
        """Empty records -> 422."""
        response = await test_client.post(
            "/api/v1/inference/vital-risk",
            headers={"Authorization": "Bearer test-bearer-token"},
            json={
                "patient_id": "P001",
                "records": [],
            },
        )

        assert response.status_code == 422

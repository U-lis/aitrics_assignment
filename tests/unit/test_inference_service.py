from datetime import UTC, datetime

from app.application.inference_service import InferenceService
from app.domain.risk_level import RiskLevel
from app.presentation.schemas.inference_schema import InferenceRequest, VitalRecord


class TestInferenceService:
    def setup_method(self):
        self.service = InferenceService()

    def test_evaluate_single_record(self):
        """Single record evaluation."""
        request = InferenceRequest(
            patient_id="P001",
            records=[
                VitalRecord(
                    recorded_at=datetime(2024, 1, 1, tzinfo=UTC),
                    vitals={"HR": 130, "SBP": 120, "SpO2": 98},
                )
            ],
        )

        response = self.service.evaluate(request)

        assert response.patient_id == "P001"
        assert response.risk_score == 0.5
        assert response.risk_level == RiskLevel.MEDIUM
        assert "HR > 120" in response.checked_rules

    def test_evaluate_multiple_returns_max(self):
        """Multiple records -> max risk_score."""
        request = InferenceRequest(
            patient_id="P001",
            records=[
                VitalRecord(
                    recorded_at=datetime(2024, 1, 1, 0, 0, tzinfo=UTC),
                    vitals={"HR": 80, "SBP": 120, "SpO2": 98},  # LOW (0.2)
                ),
                VitalRecord(
                    recorded_at=datetime(2024, 1, 1, 1, 0, tzinfo=UTC),
                    vitals={"HR": 130, "SBP": 85, "SpO2": 85},  # HIGH (0.9)
                ),
                VitalRecord(
                    recorded_at=datetime(2024, 1, 1, 2, 0, tzinfo=UTC),
                    vitals={"HR": 130, "SBP": 120, "SpO2": 98},  # MEDIUM (0.5)
                ),
            ],
        )

        response = self.service.evaluate(request)

        assert response.risk_score == 0.9
        assert response.risk_level == RiskLevel.HIGH
        assert len(response.checked_rules) == 3

    def test_response_has_evaluated_at(self):
        """Response includes evaluated_at."""
        before = datetime.now(UTC)

        request = InferenceRequest(
            patient_id="P001",
            records=[
                VitalRecord(
                    recorded_at=datetime(2024, 1, 1, tzinfo=UTC),
                    vitals={"HR": 80, "SBP": 120, "SpO2": 98},
                )
            ],
        )

        response = self.service.evaluate(request)

        after = datetime.now(UTC)
        assert before <= response.evaluated_at <= after

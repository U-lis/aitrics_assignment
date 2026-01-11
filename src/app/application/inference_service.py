from datetime import UTC, datetime

from app.domain.inference import InferenceFactory
from app.presentation.schemas.inference_schema import InferenceRequest, InferenceResponse


class InferenceService:
    def __init__(self, strategy_name: str = "rule_based"):
        self.inference = InferenceFactory.get(strategy_name)

    def evaluate(self, request: InferenceRequest) -> InferenceResponse:
        max_result = None

        for record in request.records:
            result = self.inference.evaluate(record.vitals)
            if max_result is None or result.risk_score > max_result.risk_score:
                max_result = result

        return InferenceResponse(
            patient_id=request.patient_id,
            risk_score=max_result.risk_score,
            risk_level=max_result.risk_level,
            checked_rules=max_result.checked_rules,
            evaluated_at=datetime.now(UTC),
        )

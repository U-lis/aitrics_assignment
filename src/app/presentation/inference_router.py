from fastapi import APIRouter, Depends

from app.application.inference_service import InferenceService
from app.dependencies import verify_bearer_token
from app.presentation.schemas.error_schema import ErrorResponse
from app.presentation.schemas.inference_schema import InferenceRequest, InferenceResponse

router = APIRouter(prefix="/api/v1/inference", tags=["inference"])

VITAL_RISK_DESCRIPTION = """
Evaluates patient vital signs for risk assessment using rule-based inference.

**Risk Rules:**
- HR > 120: Elevated heart rate
- SBP < 90: Low blood pressure
- SpO2 < 90: Low oxygen saturation

**Scoring:**
- 0 rules matched: LOW risk (score <= 0.3)
- 1-2 rules matched: MEDIUM risk (score 0.4-0.7)
- 3+ rules matched: HIGH risk (score >= 0.8)

When multiple records are provided, returns the highest risk assessment.
"""


@router.post(
    "/vital-risk",
    response_model=InferenceResponse,
    summary="Evaluate vital-based risk score",
    description=VITAL_RISK_DESCRIPTION,
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Invalid or missing Bearer token",
            "content": {
                "application/json": {
                    "examples": {
                        "missing_token": {
                            "summary": "No token provided",
                            "value": {"detail": "Not authenticated"},
                        },
                        "invalid_token": {
                            "summary": "Invalid token",
                            "value": {"detail": "Invalid token"},
                        },
                    }
                }
            },
        },
        422: {
            "description": "Validation error (e.g., empty records list)",
        },
    },
)
async def evaluate_vital_risk(
    request: InferenceRequest,
    _: bool = Depends(verify_bearer_token),
) -> InferenceResponse:
    service = InferenceService()
    return service.evaluate(request)

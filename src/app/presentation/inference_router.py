from fastapi import APIRouter, Depends

from app.application.inference_service import InferenceService
from app.dependencies import verify_bearer_token
from app.presentation.schemas.inference_schema import InferenceRequest, InferenceResponse

router = APIRouter(prefix="/api/v1/inference", tags=["inference"])


@router.post("/vital-risk", response_model=InferenceResponse)
async def evaluate_vital_risk(
    request: InferenceRequest,
    _: bool = Depends(verify_bearer_token),
) -> InferenceResponse:
    service = InferenceService()
    return service.evaluate(request)

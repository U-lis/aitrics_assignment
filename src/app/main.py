from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.domain.exceptions import OptimisticLockError, PatientNotFoundError, VitalNotFoundError
from app.presentation.vital_router import router as vital_router

app = FastAPI(
    title="Vital Monitor API",
    description="Hospital Vital Signs Monitoring REST API",
    version="0.1.0",
)

app.include_router(vital_router)


@app.exception_handler(VitalNotFoundError)
async def vital_not_found_handler(request: Request, exc: VitalNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(PatientNotFoundError)
async def patient_not_found_handler(request: Request, exc: PatientNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(OptimisticLockError)
async def optimistic_lock_handler(request: Request, exc: OptimisticLockError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

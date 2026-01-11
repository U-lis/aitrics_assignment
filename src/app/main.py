from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.domain.exceptions import (
    DuplicatePatientIdError,
    OptimisticLockError,
    PatientNotFoundError,
)
from app.presentation.patient_router import router as patient_router

app = FastAPI(
    title="Vital Monitor API",
    description="Hospital Vital Signs Monitoring REST API",
    version="0.1.0",
)

app.include_router(patient_router)


@app.exception_handler(PatientNotFoundError)
async def patient_not_found_handler(request: Request, exc: PatientNotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(OptimisticLockError)
async def optimistic_lock_handler(request: Request, exc: OptimisticLockError):
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(DuplicatePatientIdError)
async def duplicate_patient_handler(request: Request, exc: DuplicatePatientIdError):
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

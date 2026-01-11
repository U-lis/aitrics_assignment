from fastapi import FastAPI

from app.presentation.inference_router import router as inference_router

app = FastAPI(
    title="Vital Monitor API",
    description="Hospital Vital Signs Monitoring REST API",
    version="0.1.0",
)


app.include_router(inference_router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

from fastapi import FastAPI

app = FastAPI(
    title="Vital Monitor API",
    description="Hospital Vital Signs Monitoring REST API",
    version="0.1.0",
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

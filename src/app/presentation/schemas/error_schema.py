from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standard error response format for all API errors."""

    detail: str = Field(
        ...,
        description="Error message describing what went wrong",
        examples=["Patient P00001234 not found"],
    )

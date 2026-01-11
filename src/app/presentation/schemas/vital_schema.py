from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.domain.vital_type import VitalType


class VitalCreateRequest(BaseModel):
    patient_id: str
    recorded_at: datetime
    vital_type: VitalType
    value: float


class VitalUpdateRequest(BaseModel):
    value: float
    vital_type: VitalType
    version: int


class VitalResponse(BaseModel):
    id: UUID
    patient_id: str
    recorded_at: datetime
    vital_type: str
    value: float
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VitalItem(BaseModel):
    recorded_at: datetime
    value: float


class VitalListResponse(BaseModel):
    patient_id: str
    vital_type: str | None
    items: list[VitalItem]

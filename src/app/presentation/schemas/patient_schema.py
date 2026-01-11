from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PatientCreateRequest(BaseModel):
    patient_id: str
    name: str
    gender: Literal["M", "F"]
    birth_date: date


class PatientUpdateRequest(BaseModel):
    name: str
    gender: Literal["M", "F"]
    birth_date: date
    version: int


class PatientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    patient_id: str
    name: str
    gender: str
    birth_date: date
    version: int
    created_at: datetime
    updated_at: datetime

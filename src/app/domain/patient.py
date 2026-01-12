from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID


@dataclass
class Patient:
    """Domain entity representing a hospital patient.

    This is the core domain object independent of infrastructure concerns.
    Use this for business logic validation and domain events.
    """

    patient_id: str
    name: str
    gender: str
    birth_date: date
    id: UUID | None = None
    version: int = 1
    created_at: datetime | None = None
    updated_at: datetime | None = None

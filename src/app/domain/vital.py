from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from app.domain.vital_type import VitalType


@dataclass
class Vital:
    patient_id: str
    recorded_at: datetime
    vital_type: VitalType
    value: Decimal
    id: UUID | None = None
    version: int = 1
    created_at: datetime | None = None
    updated_at: datetime | None = None

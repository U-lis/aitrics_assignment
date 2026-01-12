from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from app.domain.vital_type import VitalType


@dataclass
class Vital:
    """Domain entity representing a vital sign measurement.

    This is the core domain object independent of infrastructure concerns.
    Use this for business logic validation and domain events.
    """

    patient_id: str
    recorded_at: datetime
    vital_type: VitalType
    value: Decimal
    id: UUID | None = None
    version: int = 1
    created_at: datetime | None = None
    updated_at: datetime | None = None

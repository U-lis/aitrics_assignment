from dataclasses import dataclass
from datetime import datetime


@dataclass
class Doctor:
    id: str
    name: str
    password_hash: str
    access_token: str | None = None
    refresh_token: str | None = None
    access_token_expires_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

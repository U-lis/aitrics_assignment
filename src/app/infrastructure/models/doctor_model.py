from datetime import UTC, datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.auth.token_encryption import decrypt_token, encrypt_token
from app.infrastructure.models.base import Base, TimestampMixin


class DoctorModel(Base, TimestampMixin):
    __tablename__ = "doctors"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    access_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    refresh_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    access_token_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    @property
    def decrypted_access_token(self) -> str | None:
        if self.access_token is None:
            return None
        return decrypt_token(self.access_token)

    @property
    def decrypted_refresh_token(self) -> str | None:
        if self.refresh_token is None:
            return None
        return decrypt_token(self.refresh_token)

    def set_tokens(self, access_token: str, refresh_token: str, expires_at: datetime) -> None:
        self.access_token = encrypt_token(access_token)
        self.refresh_token = encrypt_token(refresh_token)
        self.access_token_expires_at = expires_at

    def is_access_token_valid(self) -> bool:
        if self.access_token_expires_at is None:
            return False
        now = datetime.now(UTC)
        expires_at = self.access_token_expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        return now < expires_at

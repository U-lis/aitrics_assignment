from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt

from app.config import get_settings
from app.domain.exceptions import InvalidTokenError

ACCESS_TOKEN_JWT_EXPIRE_MINUTES = 3
ACCESS_TOKEN_DB_EXPIRE_HOURS = 1
REFRESH_TOKEN_EXPIRE_DAYS = 7


def create_access_token(doctor_id: str) -> str:
    """Create a JWT access token with 3-minute expiry."""
    settings = get_settings()
    expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_JWT_EXPIRE_MINUTES)
    payload = {
        "sub": doctor_id,
        "type": "access",
        "exp": expire,
        "iat": datetime.now(UTC),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(doctor_id: str) -> str:
    """Create a JWT refresh token with 7-day expiry."""
    settings = get_settings()
    expire = datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": doctor_id,
        "type": "refresh",
        "exp": expire,
        "iat": datetime.now(UTC),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and validate a JWT token."""
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError as e:
        raise InvalidTokenError(str(e)) from e


def get_access_token_db_expires_at() -> datetime:
    """Get the expiration time for access token in database (1 hour)."""
    return datetime.now(UTC) + timedelta(hours=ACCESS_TOKEN_DB_EXPIRE_HOURS)

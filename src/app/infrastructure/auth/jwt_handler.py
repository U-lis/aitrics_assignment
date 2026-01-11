from datetime import UTC, datetime, timedelta

from jose import ExpiredSignatureError, JWTError, jwt

from app.config import get_settings
from app.domain.exceptions import InvalidTokenError, SessionExpiredError

ACCESS_TOKEN_JWT_EXPIRE_MINUTES = 3
ACCESS_TOKEN_DB_EXPIRE_HOURS = 1
REFRESH_TOKEN_EXPIRE_DAYS = 7
IAT_FUTURE_TOLERANCE_MINUTES = 3
AUDIENCE = "aitrics"


def create_access_token(doctor_id: str) -> tuple[str, datetime]:
    """
    Create a JWT access token.

    Returns:
        tuple: (jwt_token, access_token_expires_at)
        - JWT exp = now + 3 min
        - access_token_expires_at = now + 1 hour
    """
    settings = get_settings()
    now = datetime.now(UTC)
    jwt_expire = now + timedelta(minutes=ACCESS_TOKEN_JWT_EXPIRE_MINUTES)
    db_expires_at = now + timedelta(hours=ACCESS_TOKEN_DB_EXPIRE_HOURS)

    payload = {
        "iat": now,
        "exp": jwt_expire,
        "iss": doctor_id,
        "aud": AUDIENCE,
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, db_expires_at


def create_refresh_token(doctor_id: str) -> str:
    """Create a JWT refresh token with 7-day expiry."""
    settings = get_settings()
    now = datetime.now(UTC)
    expire = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    payload = {
        "iat": now,
        "exp": expire,
        "iss": doctor_id,
        "aud": AUDIENCE,
        "type": "refresh",
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """
    Decode and validate a JWT token.

    Validates:
    - Signature
    - Expiration (exp)
    - Audience (aud == "aitrics")
    - Issued at not too far in future (iat <= now + 3min)

    Raises:
        SessionExpiredError: If token is expired
        InvalidTokenError: If token is invalid (signature, audience, future iat)
    """
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            audience=AUDIENCE,
        )

        # Check iat is not too far in the future
        iat = payload.get("iat")
        if iat:
            iat_dt = datetime.fromtimestamp(iat, tz=UTC)
            max_allowed_iat = datetime.now(UTC) + timedelta(minutes=IAT_FUTURE_TOLERANCE_MINUTES)
            if iat_dt > max_allowed_iat:
                raise InvalidTokenError("Token issued at time is too far in the future")

        return payload
    except ExpiredSignatureError as e:
        raise SessionExpiredError("Token has expired") from e
    except JWTError as e:
        raise InvalidTokenError(str(e)) from e


def get_access_token_db_expires_at() -> datetime:
    """Get the expiration time for access token in database (1 hour)."""
    return datetime.now(UTC) + timedelta(hours=ACCESS_TOKEN_DB_EXPIRE_HOURS)

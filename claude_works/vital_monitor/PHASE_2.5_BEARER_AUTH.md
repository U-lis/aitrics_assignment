# Phase 2.5: Auth Migration (JWT to Static Bearer Token)

## Goal

Migrate from JWT-based doctor authentication to static Bearer token for server-to-server communication.

## Context

- Service environment changed to server-to-server communication
- JWT complexity no longer needed
- Simple Bearer token validation is sufficient

## Instructions

### Step 1: Delete Files

Remove the following 15 files:

**Application Layer:**
- [ ] `src/app/application/auth_service.py`

**Presentation Layer:**
- [ ] `src/app/presentation/auth_router.py`
- [ ] `src/app/presentation/schemas/auth_schema.py`

**Infrastructure Layer:**
- [ ] `src/app/infrastructure/models/doctor_model.py`
- [ ] `src/app/infrastructure/repositories/doctor_repository.py`
- [ ] `src/app/infrastructure/auth/jwt_handler.py`
- [ ] `src/app/infrastructure/auth/token_encryption.py`
- [ ] `src/app/infrastructure/auth/password_handler.py`

**Domain Layer:**
- [ ] `src/app/domain/doctor.py`

**Tests:**
- [ ] `tests/unit/test_auth_service.py`
- [ ] `tests/unit/test_jwt_handler.py`
- [ ] `tests/unit/test_token_encryption.py`
- [ ] `tests/unit/test_password_handler.py`
- [ ] `tests/e2e/test_auth_api.py`

### Step 2: Modify Files

**`src/app/config.py`**
- [ ] Remove: `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `AES_SECRET_KEY`
- [ ] Add: `BEARER_TOKEN: str`

**`src/app/main.py`**
- [ ] Remove: `auth_router` import and include
- [ ] Remove: `/me` endpoint
- [ ] Remove: `get_current_doctor` import and usage

**`src/app/dependencies.py`**
- [ ] Replace entire content with simple Bearer token validation:

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import get_settings

security = HTTPBearer()


def verify_bearer_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> bool:
    """
    Verify Bearer token matches configured token.

    Raises:
        HTTPException 401: If token is invalid or missing
    """
    settings = get_settings()
    if credentials.credentials != settings.BEARER_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return True
```

**`src/app/domain/exceptions.py`**
- [ ] Remove: `DoctorNotFoundError`
- [ ] Remove: `InvalidCredentialsError`
- [ ] Remove: `DuplicateDoctorIdError`
- [ ] Keep: `InvalidTokenError`, `SessionExpiredError` (may be useful)

**`src/app/infrastructure/models/__init__.py`**
- [ ] Remove: `DoctorModel` import and `__all__` entry

**`.env.example`**
- [ ] Remove: `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `AES_SECRET_KEY`
- [ ] Add: `BEARER_TOKEN=your-secure-bearer-token-here`

**`pyproject.toml`**
- [ ] Remove from dependencies:
  - `python-jose[cryptography]`
  - `argon2-cffi`
  - `pycryptodome`

### Step 3: Create Migration

Create `alembic/versions/xxx_drop_doctors_table.py`:

```python
"""Drop doctors table

Revision ID: {auto-generated}
Revises: 1e6b7927b28f
Create Date: {auto-generated}
"""

from collections.abc import Sequence

from alembic import op

revision: str = "{auto-generated}"
down_revision: str | Sequence[str] | None = "1e6b7927b28f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_table("doctors")


def downgrade() -> None:
    # doctors table recreation not supported
    # This is a one-way migration
    pass
```

### Step 4: Create Tests

Create `tests/unit/test_bearer_auth.py`:

- [ ] Test: Valid token returns success (dependency returns True)
- [ ] Test: Invalid token raises 401 HTTPException
- [ ] Test: Missing token raises 401 HTTPException

### Step 5: Update conftest.py

- [ ] Remove any doctor-related fixtures if present
- [ ] Add `BEARER_TOKEN` to test settings override

## Verification Checklist

- [ ] `uv sync` - Dependencies updated successfully
- [ ] `uv run alembic upgrade head` - Migration succeeds
- [ ] `uv run ruff check src tests` - No lint errors
- [ ] `uv run ty src` - No type errors
- [ ] `uv run pytest` - All tests pass, coverage >= 75%
- [ ] Manual test: `curl -H "Authorization: Bearer <token>" http://localhost:8000/health`

## Notes

- User must update `.env` with `BEARER_TOKEN` value after implementation
- Existing doctor data in DB will be dropped
- downgrade() in migration is intentionally empty (one-way migration)

# Phase 2: Authentication

## Objective

Implement doctor registration, login, and JWT token management.

## APIs

- `POST /auth/register` - Create doctor account
- `POST /auth/login` - Issue access_token + refresh_token
- `POST /auth/refresh-token` - Refresh access_token

## Tasks

### 1. Create password_handler.py (argon2)

Location: `src/app/infrastructure/auth/password_handler.py`

```python
def hash_password(password: str) -> str:
    """Hash password using argon2"""

def verify_password(password: str, hash: str) -> bool:
    """Verify password against hash"""
```

### 2. Create token_encryption.py (AES-256)

Location: `src/app/infrastructure/auth/token_encryption.py`

```python
def encrypt_token(token: str) -> str:
    """Encrypt token using AES-256 with AES_SECRET_KEY from env"""

def decrypt_token(encrypted: str) -> str:
    """Decrypt token"""
```

### 3. Create jwt_handler.py

Location: `src/app/infrastructure/auth/jwt_handler.py`

**Token Structure:**
```json
{
  "iat": "current_timestamp",
  "exp": "current_timestamp + 3min",
  "iss": "doctor.id",
  "aud": "aitrics"
}
```

**Functions:**
```python
def create_access_token(doctor_id: str) -> tuple[str, datetime]:
    """
    Returns (jwt_token, access_token_expires_at)
    - JWT exp = now + 3 min
    - access_token_expires_at = now + 1 hour
    """

def create_refresh_token(doctor_id: str) -> str:
    """Create refresh token"""

async def verify_token(token: str, db_session) -> dict:
    """
    Verify JWT token. Reject if:
    - Signature mismatch
    - JWT exp < now (need refresh)
    - iat > now + 3min (future timestamp)
    - Token != doctor's stored access_token
    """
```

### 4. Create AuthService

Location: `src/app/application/auth_service.py`

**register(id, password, name):**
- Check if doctor id already exists
- Hash password with argon2
- Create doctor record

**login(id, password):**
```python
# Verify credentials
if not verify_password(password, doctor.password_hash):
    raise InvalidCredentialsError

# Check if session (access_token_expires_at) is still valid
if doctor.is_access_token_valid():
    # Return existing token (JWT may be expired, client should refresh)
    return {
        "access_token": doctor.decrypted_access_token,
        "refresh_token": doctor.decrypted_refresh_token,
        "expires_at": doctor.access_token_expires_at
    }

# Generate new tokens
access_token, expires_at = create_access_token(doctor.id)
refresh_token = create_refresh_token(doctor.id)
doctor.set_tokens(access_token, refresh_token, expires_at)
return {"access_token": access_token, "refresh_token": refresh_token, "expires_at": expires_at}
```

**refresh(refresh_token):**
```python
# Verify refresh_token matches stored one
if refresh_token != doctor.decrypted_refresh_token:
    raise InvalidTokenError

if doctor.is_access_token_valid():
    # Within 1 hour: reuse period, just re-sign JWT
    new_access_token = create_jwt(doctor.id, exp=now+3min)
    doctor.access_token = encrypt(new_access_token)
    return {"access_token": new_access_token, "expires_at": doctor.access_token_expires_at}
else:
    # After 1 hour: issue new access_token with new 1-hour period
    new_access_token, new_expires_at = create_access_token(doctor.id)
    doctor.access_token = encrypt(new_access_token)
    doctor.access_token_expires_at = new_expires_at
    return {"access_token": new_access_token, "expires_at": new_expires_at}
```

### 5. Create Auth Schemas

Location: `src/app/presentation/schemas/auth_schema.py`

- RegisterRequest: id, password, name
- RegisterResponse: id, name, created_at
- LoginRequest: id, password
- LoginResponse: access_token, refresh_token, expires_at
- RefreshRequest: refresh_token
- RefreshResponse: access_token, expires_at

### 6. Create Auth Router

Location: `src/app/presentation/auth_router.py`

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh-token`

### 7. Create Auth Dependency

Location: `src/app/dependencies.py`

```python
async def get_current_doctor(
    authorization: str = Header(..., alias="Authorization"),
    db: AsyncSession = Depends(get_db_session)
) -> Doctor:
    """
    Extract Bearer token, verify, return doctor.
    Raise 401 on any failure.
    """
```

## Token Lifecycle Reference

```
[Login] -> access_token issued (reusable for 1 hour)
             └── JWT signed with exp = now + 3min

[After 3min] -> JWT signature validation fails
                └── Call /auth/refresh-token
                └── Same access_token value, new JWT signature

[After 1 hour] -> access_token_expires_at reached
                  └── Call /auth/refresh-token
                  └── New access_token issued (new 1 hour period)
                  └── Login NOT required
```

## Checklist

- [x] password_handler.py created (argon2)
- [x] token_encryption.py created (AES-256-GCM)
- [x] jwt_handler.py created
- [x] AuthService created with register/login/refresh
- [x] Auth schemas created
- [x] Auth router created
- [x] Auth dependency (get_current_doctor) created
- [x] 401 responses on auth failure

## Test Cases

### Password Handler (tests/unit/test_password_handler.py)

| Test | Description |
|------|-------------|
| test_hash_password | Hash succeeds |
| test_hash_password_different_each_time | Same password → different hashes (salt) |
| test_verify_password_success | Correct password verifies |
| test_verify_password_failure | Wrong password fails |

### Token Encryption (tests/unit/test_token_encryption.py)

| Test | Description |
|------|-------------|
| test_encrypt_token | Encryption succeeds |
| test_decrypt_token | Decryption returns original |
| test_encrypted_differs_from_original | Encrypted ≠ original |

### JWT Handler (tests/unit/test_jwt_handler.py)

| Test | Description |
|------|-------------|
| test_create_access_token | Returns (token, expires_at) |
| test_create_access_token_exp_3min | JWT exp = now + 3min |
| test_create_access_token_expires_at_1hour | expires_at = now + 1hour |
| test_create_refresh_token | Creates refresh token |
| test_verify_token_success | Valid token passes |
| test_verify_token_expired | Create JWT with iat/exp = now - 5min → TokenExpiredError |
| test_verify_token_future_iat | iat > now + 3min → InvalidTokenError |
| test_verify_token_wrong_audience | aud ≠ "aitrics" → InvalidTokenError |
| test_verify_token_mismatch_stored | Token ≠ DB stored → InvalidTokenError |

### Auth API E2E (tests/e2e/test_auth_api.py)

| Test | Description |
|------|-------------|
| test_register_success | POST /auth/register → 201 |
| test_register_duplicate_id | Duplicate ID → 409 |
| test_login_success | POST /auth/login → 200 with tokens |
| test_login_invalid_id | Unknown ID → 401 |
| test_login_wrong_password | Wrong password → 401 |
| test_login_returns_existing_token | Valid session → same token returned |
| test_refresh_success | POST /auth/refresh-token → 200 |
| test_refresh_invalid_token | Invalid refresh_token → 401 |
| test_refresh_within_1hour | Same expires_at, new JWT |
| test_refresh_after_1hour | Set access_token_expires_at = now - 1hour → new expires_at |

# Phase 0: Planning

## session_0_1

**Date: 2026-01-11**

### Initial Planning Discussion

**User Request:**

- Build Hospital Vital Signs Monitoring API based on spec.md
- Development order: DB modeling > schema/API > containerize

**Tech Stack Decisions:**
| Component | Choice | Reason |
|-----------|--------|--------|
| Framework | FastAPI | async, OpenAPI auto-gen, Pydantic integration |
| Database | PostgreSQL | production-ready, Docker compatible |
| Auth | JWT | User selected over static token |

**Inference Logic Decision:**

- When multiple records in request: evaluate each separately, return max risk_score

---

### User Feedback on Initial Plan

**Phase 0.5 Addition Request:**

- Add development environment setup phase
- Required packages: dotenv, pytest, coverage, alembic

**Work Order Revision:**

- User proposal: Phase 1 (DB) -> 2 (Auth) -> 3A, 3B, 3C parallel
- Rationale: After DB and Auth are ready, Patient/Vital/Inference APIs can be developed in parallel

**Containerization Requirements:**

1. Auto-run alembic migrate on service startup
2. External access path required (e.g., localhost:8080)

**DB Model Updates:**

1. All datetime stored in UTC
2. created_at: auto UTCNOW on insert
3. updated_at: auto UTCNOW on insert/update

---

### Doctor Model & Auth System (Detailed)

**doctors table:**
| Column | Type | Notes |
|--------|------|-------|
| id | VARCHAR(50) | PK, doctor login ID |
| password_hash | VARCHAR(255) | argon2 hashed |
| name | VARCHAR(100) | |
| access_token | TEXT | AES-256 encrypted |
| refresh_token | TEXT | AES-256 encrypted |
| access_token_expires_at | TIMESTAMPTZ | Token reuse period |

**DoctorModel Helpers:**

- `decrypted_access_token` property: Get plaintext access_token
- `decrypted_refresh_token` property: Get plaintext refresh_token
- `set_tokens()`: Encrypt and store tokens
- `is_access_token_valid()`: Check if access_token_expires_at > now

**Auth APIs:**

- `POST /auth/register`: Create doctor account
- `POST /auth/login`: Issue access_token + refresh_token
- `POST /auth/refresh-token`: Refresh access_token

**JWT Structure:**

```json
{
  "iat": "current_timestamp",
  "exp": "current_timestamp + 3min",
  "iss": "doctor.id",
  "aud": "aitrics"
}
```

---

### Token Expiration Clarification (Critical)

**Two Different Expiration Concepts:**
| Concept | Duration | Purpose |
|---------|----------|---------|
| `access_token_expires_at` (DB) | 1 hour | Token reuse period |
| JWT `exp` field | 3 min | JWT signature validation |

**Token Lifecycle:**

```
[Login] -> access_token issued (reusable for 1 hour)
             └── JWT signed with exp = now + 3min

[After 3min] -> JWT signature validation fails (exp passed)
                └── Call /auth/refresh-token
                └── Same access_token value, new JWT signature

[After 1 hour] -> access_token_expires_at reached
                  └── Call /auth/refresh-token
                  └── New access_token issued (new 1 hour period)
                  └── Login NOT required, refresh_token still valid
```

**Key Point:** JWT `exp` is for signature validation only, not token expiration.
Token remains valid as long as refresh_token is valid.

**Token Validation Rules (reject if any):**

- Signature mismatch
- JWT exp < now (need refresh)
- iat > now + 3min (future timestamp)
- Token != doctor's stored access_token (DB lookup by iss)

---

### Additional Refinements

**Vital Update API:**

- Added `vital_type` field to VitalUpdateRequest schema

**Inference Strategy Pattern:**

- BaseInference ABC with evaluate() method
- RuleBasedInference implementation
- InferenceFactory for strategy selection
- Allows future replacement of inference algorithm

---

## session_0_2

**Date: 2026-01-11**

### Test Strategy Discussion

**User Requirements:**

1. Test coverage >= 75%
2. DB tests: Create test DB, run `alembic upgrade head` at start, `alembic downgrade base` at end
3. API e2e tests: Direct API calls preferred over mocking

**Time-related Test Solutions (User Decision):**
| Test Scenario | Solution |
|---------------|----------|
| JWT expiration (3min) | Create JWT with iat/exp = now - 5min |
| access_token expiration (1h) | Set access_token_expires_at = now - 1hour in DB |

**Phase 4 Testing:**

- Manual verification only
- Add README.md with usage documentation

**Test DB:**

- Name: `vital_monitor_test`

---

### Test Infrastructure Design

**Test Fixtures (conftest.py):**

- `setup_database` (session scope): alembic upgrade/downgrade
- `db_session` (function scope): transaction rollback per test
- `client`: FastAPI TestClient with DB override
- `auth_client`: Pre-authenticated client

**Test Directory Structure:**

```
tests/
├── conftest.py
├── unit/
│   ├── test_password_handler.py
│   ├── test_token_encryption.py
│   ├── test_jwt_handler.py
│   ├── test_rule_based_inference.py
│   └── test_inference_factory.py
└── e2e/
    ├── test_auth_api.py
    ├── test_patient_api.py
    ├── test_vital_api.py
    └── test_inference_api.py
```

---

### Test Case Summary

| Phase          | Test Count | Type       |
|----------------|------------|------------|
| 1 (Database)   | 15         | Unit       |
| 2 (Auth)       | 22         | Unit + E2E |
| 3A (Patient)   | 8          | E2E        |
| 3B (Vital)     | 13         | E2E        |
| 3C (Inference) | 15         | Unit + E2E |
| **Total**      | **73**     |            |

**Status:** Test cases finalized, phase md files being updated

---

# Phase 0.5: Environment Setup

## session_0.5_1

**Date: 2026-01-11**

### Additional Requirements

**User Request:**
Add linter, formatter, type checker, and pre-commit hooks to Phase 0.5.

**Tool Decisions:**
| Tool | Purpose | Notes |
|------|---------|-------|
| ruff | Linter + Formatter | Single tool for both |
| ty | Type Checker | Astral's new type checker |
| pre-commit | Git hooks | Automate quality checks |

**Pre-commit Hook Configuration:**
| Hook Stage | Action |
|------------|--------|
| pre-commit | ruff lint + format |
| pre-push | pytest (all tests must pass) |

**Status:** Phase 0.5 md file to be updated with these requirements

---

## session_0.5_2

**Date: 2026-01-11**

### Execution & Completed Work

**Work Completed:**

- Phase 0.5 environment setup executed successfully
- All dependencies installed via `uv sync --all-extras`
- Pre-commit hooks installed (pre-commit: ruff, pre-push: pytest)
- ruff, ty verified working correctly

**Additional Requirements During Execution:**
| Requirement | Action Taken |
|-------------|--------------|
| Coverage >= 75% | Added `--cov-fail-under=75` to pytest config |
| README .env setup guide | Added "How to use" section with key generation examples |
| ipython for dev | Added to dev dependencies |

**Key Generation Examples Added to README:**

```bash
# JWT secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# AES-256 key (32 bytes, base64 encoded)
python -c "import os, base64; print(base64.b64encode(os.urandom(32)).decode())"
```

**User Action Required:**

- Copy `.env.example` to `.env` and configure actual values

**Status:** Phase 0.5 completed, ready for Phase 1

---

# Phase 5: CI Pipeline

## session_5_1

**Date: 2026-01-11**

### CI Pipeline Requirements

**User Request:**
Add Phase 5 for GitHub Actions CI pipeline to validate code quality on push/PR.

**CI Tools:**
| Tool | Purpose |
|------|---------|
| ruff | Linting + Formatting check |
| ty | Type checking (Astral's Python type checker) |
| pytest | Test execution with PostgreSQL |

**User Decisions:**
| Option | Choice |
|--------|--------|
| Type checker | ty (alpha, but recommended for Astral ecosystem consistency) |
| Trigger branches | All branches (push and PR) |
| Coverage reporting | Codecov integration included |

**Workflow Structure:**

- 3 parallel jobs: `lint`, `typecheck`, `test`
- PostgreSQL service container for test job
- UV caching via `astral-sh/setup-uv@v5`

**Status:** Phase 5 md file and GLOBAL.md to be created/updated

---

# Phase 1: Database Foundation

## session_1_1

**Date: 2026-01-11**

### Phase 1 Execution

**Work Completed:**

1. Created `src/app/config.py` with pydantic-settings
2. Created `src/app/infrastructure/database.py` with async SQLAlchemy
3. Created Base model with TimestampMixin
4. Created ORM models: DoctorModel, PatientModel, VitalModel
5. Created Domain entities and enums
6. Created auth utilities (token_encryption, password_handler, jwt_handler)
7. Initialized Alembic with async PostgreSQL support
8. Created repository interfaces
9. Wrote and executed 16 unit tests (all passed)

**Technical Decisions:**

| Issue | Solution | Reason |
|-------|----------|--------|
| `server_default` with asyncpg | Use `text("gen_random_uuid()")` | asyncpg interprets string literals differently |
| Pydantic v2 deprecation | `class Config` → `model_config = SettingsConfigDict(...)` | Future compatibility |
| All datetime columns | `DateTime(timezone=True)` | GLOBAL.md requirement: UTC storage |

**Migrations Created:**

1. `5843dbdd935f_initial_tables.py`: doctors, patients, vitals tables
2. `1e6b7927b28f_add_timezone_to_access_token_expires_at.py`: Fix timezone for DoctorModel

---

### ty Type Checker Issues & Fixes

**Initial Errors (4):**

| Error | File | Cause |
|-------|------|-------|
| `missing-argument` | config.py | pydantic-settings loads from .env, ty unaware |
| `unsupported-operator` | token_encryption.py | `cipher.iv` type is `bytes \| bytearray \| memoryview` |
| `no-matching-overload` | patient_model.py | SQLAlchemy UUID overload type definition |
| `no-matching-overload` | vital_model.py | Same as above |

**Solutions Applied:**

| File | Fix |
|------|-----|
| config.py | Added `# ty: ignore[missing-argument]` comment |
| token_encryption.py | `cipher.iv + encrypted` → `bytes(cipher.iv) + encrypted` |
| patient_model.py | `UUID(as_uuid=True)` → `Uuid` (SQLAlchemy 2.0 type) |
| vital_model.py | Same as patient_model.py |

**Final Results:**

| Tool | Result |
|------|--------|
| ruff lint | ✅ All checks passed |
| ruff format | ✅ No changes needed |
| ty check | ✅ All checks passed |
| pytest | ✅ 16 passed, coverage 57% |

**Note:** Coverage 57% is expected - service layer and API endpoints not yet implemented.

**Status:** Phase 1 completed, GLOBAL.md and PHASE_1_DATABASE.md updated

---

# Phase 2: Authentication (JWT)

## session_2_1

**Date: 2026-01-11**

### Phase 2 Execution

**Work Completed:**

1. Updated token_encryption.py from AES-256-CBC to AES-256-GCM (user request)
2. Updated jwt_handler.py with Phase 2 spec (iss/aud claims, tuple return)
3. Created AuthService with register/login/refresh methods
4. Created auth schemas (RegisterRequest/Response, LoginRequest/Response, RefreshRequest/Response)
5. Created auth_router.py with /auth/register, /auth/login, /auth/refresh-token endpoints
6. Created dependencies.py with get_current_doctor dependency
7. Created main.py FastAPI application
8. Wrote and executed 66 tests (all passed, 75.29% coverage)

**Technical Decisions:**

| Issue | Solution |
|-------|----------|
| AES encryption mode | AES-256-GCM (user explicitly requested instead of CBC) |
| JWT exp microsecond precision | JWT library truncates to seconds, use `.replace(microsecond=0)` in tests |
| HTTPBearer 401 vs 403 | HTTPBearer returns 401 for missing token, not 403 |
| B008 ruff warning | Added `ignore = ["B008"]` for FastAPI Depends() pattern |
| Import path without PYTHONPATH | Added `pythonpath = ["src"]` to pyproject.toml |

**Status:** Phase 2 completed

---

# Phase 2.5: Auth Migration (JWT to Bearer Token)

## session_2.5_1

**Date: 2026-01-11**

### Architecture Change Decision

**Context Change:**
Service environment changed to **Server-to-Server** communication. JWT-based authentication is no longer necessary. Simple Bearer token validation is sufficient for security.

**User Requirements:**

1. Delete doctor model and related APIs
2. Remove JWT auth related `.env` settings and validation logic
3. Add Bearer token matching validation logic

### Clarification Questions & Answers

**Q1: How will the Bearer token be managed?**
- Options: `.env fixed token` / `System env var` / `Dynamic token exchange`
- **Answer**: `.env fixed token` - Same token configured in both servers' .env files

**Q2: How to handle doctors table in DB?**
- Options: `Create DROP migration` / `Reset DB entirely`
- **Answer**: `Create DROP migration` - Create new migration file to drop doctors table

**Q3: Is `/me` endpoint (authenticated user info) needed?**
- Options: `Delete` / `Keep (simplified)`
- **Answer**: `Delete` - It was only for auth testing

### Impact Analysis

**Files to DELETE (15 files):**
- `src/app/application/auth_service.py`
- `src/app/presentation/auth_router.py`
- `src/app/presentation/schemas/auth_schema.py`
- `src/app/infrastructure/models/doctor_model.py`
- `src/app/infrastructure/repositories/doctor_repository.py`
- `src/app/infrastructure/auth/jwt_handler.py`
- `src/app/infrastructure/auth/token_encryption.py`
- `src/app/infrastructure/auth/password_handler.py`
- `src/app/domain/doctor.py`
- `tests/unit/test_auth_service.py`
- `tests/unit/test_jwt_handler.py`
- `tests/unit/test_token_encryption.py`
- `tests/unit/test_password_handler.py`
- `tests/e2e/test_auth_api.py`

**Files to MODIFY:**
- `src/app/config.py` - Remove JWT/AES settings, add `BEARER_TOKEN`
- `src/app/main.py` - Remove auth_router, /me endpoint
- `src/app/dependencies.py` - Simple token comparison instead of JWT validation
- `src/app/domain/exceptions.py` - Remove Doctor-related exceptions
- `src/app/infrastructure/models/__init__.py` - Remove DoctorModel export
- `.env.example` - Update settings
- `pyproject.toml` - Remove unused dependencies

**Files to CREATE:**
- `alembic/versions/xxx_drop_doctors_table.py` - Migration to drop doctors table
- `tests/unit/test_bearer_auth.py` - New auth tests

**Dependencies to REMOVE:**
- `python-jose[cryptography]`
- `argon2-cffi`
- `pycryptodome`

### New Authentication Flow

```
Request -> HTTPBearer extracts token -> Compare with settings.BEARER_TOKEN
                                     -> Match: Continue to endpoint
                                     -> No match: Raise 401 Unauthorized
```

**Status:** Phase 2.5 planning completed, pending execution

---

# Phase 3B: Vital Data API

## session_3b_1

**Date: 2026-01-11**

### Task Request

User requested to read GLOBAL.md and PHASE_3B_VITAL_API.md, then implement Phase 3B (Vital Data API).

### Codebase Exploration

**Already Implemented (from previous phases):**
| Component | Location | Status |
|-----------|----------|--------|
| VitalType enum | `domain/vital_type.py` | ✅ Ready |
| Domain exceptions | `domain/exceptions.py` | ✅ Ready |
| VitalModel | `infrastructure/models/vital_model.py` | ✅ Ready |
| VitalRepository | `infrastructure/repositories/vital_repository.py` | ✅ Ready |
| PatientRepository | `infrastructure/repositories/patient_repository.py` | ✅ Ready |
| Auth dependency | `dependencies.py` | ✅ Ready |
| Test fixtures | `tests/conftest.py` | ✅ Ready |

**Needs Implementation:**
- Vital schemas (presentation layer)
- VitalService (application layer)
- Vital router (presentation layer)
- Exception handlers in main.py
- E2E tests

### Implementation

**Files Created:**
| File | Description |
|------|-------------|
| `src/app/presentation/__init__.py` | Package init |
| `src/app/presentation/schemas/__init__.py` | Package init |
| `src/app/presentation/schemas/vital_schema.py` | 5 Pydantic schemas |
| `src/app/application/__init__.py` | Package init |
| `src/app/application/vital_service.py` | VitalService class |
| `src/app/presentation/vital_router.py` | 3 API endpoints |
| `tests/e2e/__init__.py` | Package init |
| `tests/e2e/test_vital_api.py` | 13 E2E tests |
| `tests/unit/test_vital_service.py` | 7 unit tests |

**Files Modified:**
| File | Changes |
|------|---------|
| `src/app/main.py` | Added exception handlers + vital_router |

### API Endpoints

| Method | Path | Status Code | Description |
|--------|------|-------------|-------------|
| POST | `/api/v1/vitals` | 201 | Create vital |
| GET | `/api/v1/patients/{patient_id}/vitals` | 200 | Query with time range/type filter |
| PUT | `/api/v1/vitals/{vital_id}` | 200 | Update with optimistic lock |

### Issues Encountered & Resolved

| Issue | Cause | Solution |
|-------|-------|----------|
| Event loop conflict | Used `@pytest.mark.anyio` instead of `@pytest.mark.asyncio` | Changed to `@pytest.mark.asyncio` |
| DB session isolation | Fixture data not visible to API | Used explicit commits and unique patient_ids |
| Auth status code | Expected 403, got 401 | Corrected test to expect 401 |
| Coverage 73% < 75% | Missing unit tests | Added 7 VitalService unit tests |

### Test Results

```
32 passed
Coverage: 79.42% (target: >= 75%)
```

### Checklist Updates

Updated PHASE_3B_VITAL_API.md:
```markdown
- [x] Vital schemas created (with vital_type in update)
- [x] VitalService created
- [x] Vital router created
- [x] Patient validation on vital create
- [x] Time range query implemented
- [x] Optional vital_type filter
- [x] Auth dependency applied to all routes
- [x] 409 Conflict on version mismatch
```

Updated GLOBAL.md Phase Overview:
```
| 3B | Vital Data API | 2.5 | **Completed** |
```

**Status:** Phase 3B completed successfully

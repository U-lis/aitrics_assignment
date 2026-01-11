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

# Phase 3A: Patient API

## session_3A_1

**Date: 2026-01-11**

### Phase 3A Execution

**Work Completed:**

1. Created presentation schemas (`patient_schema.py`)
   - `PatientCreateRequest`: patient_id, name, gender, birth_date
   - `PatientUpdateRequest`: name, gender, birth_date, version
   - `PatientResponse`: Full patient data with timestamps

2. Created application service (`patient_service.py`)
   - `create_patient()`: Duplicate check + create
   - `update_patient()`: Optimistic lock with version check

3. Created patient router (`patient_router.py`)
   - `POST /api/v1/patients` → 201 Created
   - `PUT /api/v1/patients/{patient_id}` → 200 OK

4. Registered exception handlers in `main.py`
   - `OptimisticLockError` → 409 Conflict
   - `PatientNotFoundError` → 404 Not Found
   - `DuplicatePatientIdError` → 409 Conflict

5. Wrote E2E tests (`test_patient_api.py`) - 8 tests

6. Added unit tests for optimistic locking (`test_repositories.py`) - 2 tests

**Technical Issues & Solutions:**

| Issue | Solution |
|-------|----------|
| pytest-asyncio event loop mismatch | Added `asyncio_default_test_loop_scope = "session"` to pyproject.toml |
| database.py module-level engine creation | Refactored to lazy initialization pattern |
| HTTPBearer returns 401 (not 403) for missing token | Fixed test expectations |

**Configuration Changes:**

| File | Change |
|------|--------|
| `pyproject.toml` | Added `asyncio_default_fixture_loop_scope = "session"`, `asyncio_default_test_loop_scope = "session"` |
| `src/app/infrastructure/database.py` | Converted to lazy initialization (`_engine`, `_async_session_factory` globals) |
| `tests/conftest.py` | Added `reset_database_globals` fixture, session-scoped `test_engine` |

### Coverage Analysis

**Final Results:**
- 22 tests passed
- Coverage: 70% (target: 75%)

**Coverage Gap Reasons:**

| File | Coverage | Reason |
|------|----------|--------|
| `domain/patient.py` | 0% | Dataclass not directly used (PatientModel used instead) |
| `domain/vital.py` | 0% | Phase 3B - not yet implemented |
| `domain/risk_level.py` | 0% | Phase 3C - not yet implemented |
| `infrastructure/database.py` | 47% | Lazy init functions overridden in tests |
| `repositories/vital_repository.py` | 50% | Phase 3B - not yet implemented |

**Conclusion:** 75% coverage will be achieved after Phase 3B/3C completion. Current 70% is expected for Phase 3A scope.

### Optimistic Lock Test Coverage

| Layer | Test | Status |
|-------|------|--------|
| Unit | `test_patient_repo_update_with_version_success` | ✅ Added |
| Unit | `test_patient_repo_update_with_version_conflict` | ✅ Added |
| E2E | `test_update_patient_version_increment` | ✅ |
| E2E | `test_update_patient_optimistic_lock_conflict` | ✅ |

**Status:** Phase 3A completed, all checklist items verified

---

## session_3A_2

**Date: 2026-01-11**

### Code Review: database.py Changes

**User Concern:**
`database.py` changes (lazy initialization) are too extensive and may cause conflicts with other branches.

**Analysis:**

Original issue was pytest-asyncio event loop mismatch. Two changes were made:
1. `pyproject.toml`: Added `asyncio_default_*_loop_scope = "session"`
2. `database.py`: Converted to lazy initialization pattern

**Question:** Was database.py change actually necessary?

| Factor | Analysis |
|--------|----------|
| Test behavior | `get_db_session` is overridden in tests, so original engine is never used |
| Root cause | Event loop mismatch fixed by pyproject.toml settings alone |
| Branch impact | Lazy init adds complexity and potential merge conflicts |

**Conclusion:** `database.py` change was unnecessary. The `pyproject.toml` settings alone fix the issue.

### Revert Decision

**User Decision:** Revert unnecessary changes.

**Changes Reverted:**

| File | Action |
|------|--------|
| `database.py` | Reverted to original (module-level engine creation) |
| `conftest.py` | Removed `reset_database_globals` fixture |

**Kept Changes:**

| File | Setting |
|------|---------|
| `pyproject.toml` | `asyncio_default_fixture_loop_scope = "session"` |
| `pyproject.toml` | `asyncio_default_test_loop_scope = "session"` |

### Test Results After Revert

```
22 passed
Coverage: 72% (improved from 70% due to simpler database.py)
```

**Key Learning:** The actual fix for pytest-asyncio event loop issues is the loop scope configuration, not lazy initialization of database engines.

**Status:** Phase 3A finalized, GLOBAL.md updated to mark as Completed

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

---

# Phase 3C: Inference API

## session_3c_1

**Date: 2026-01-11**

### Phase 3C Execution

**Objective:**
Implement rule-based vital risk scoring API with pluggable strategy pattern.

**Work Completed:**

1. Created inference domain layer (Strategy Pattern):
   - `src/app/domain/inference/base.py` - BaseInference ABC + InferenceResult dataclass
   - `src/app/domain/inference/rule_based_inference.py` - RuleBasedInference implementation
   - `src/app/domain/inference/factory.py` - InferenceFactory for strategy selection
   - `src/app/domain/inference/__init__.py` - Public exports

2. Created application layer:
   - `src/app/application/__init__.py`
   - `src/app/application/inference_service.py` - InferenceService with multi-record handling

3. Created presentation layer:
   - `src/app/presentation/__init__.py`
   - `src/app/presentation/schemas/__init__.py`
   - `src/app/presentation/schemas/inference_schema.py` - VitalRecord, InferenceRequest, InferenceResponse
   - `src/app/presentation/inference_router.py` - POST /api/v1/inference/vital-risk

4. Updated `src/app/main.py` - Registered inference_router

5. Created tests:
   - `tests/unit/test_rule_based_inference.py` - 9 tests
   - `tests/unit/test_inference_factory.py` - 3 tests
   - `tests/unit/test_inference_service.py` - 3 tests
   - `tests/e2e/test_inference_api.py` - 4 tests
   - `tests/e2e/conftest.py` - E2E test fixture without DB dependency

**Risk Scoring Logic:**

| Matched Rules | Score | Level |
|---------------|-------|-------|
| 0 | 0.2 | LOW |
| 1 | 0.5 | MEDIUM |
| 2 | 0.7 | MEDIUM |
| 3+ | 0.9 | HIGH |

**Rules Implemented:**
- HR > 120 → Risk increase
- SBP < 90 → Risk increase
- SpO2 < 90 → Risk increase

**Multi-record Handling:**
- Evaluate each record separately
- Return highest risk_score among all evaluations

**Test Results:**
```
19 passed in 0.04s
```

**Technical Decisions:**

| Issue | Solution |
|-------|----------|
| E2E tests conflicting with DB conftest | Created separate `tests/e2e/conftest.py` with DB-independent fixture |
| RiskLevel type consistency | Used `RiskLevel` enum from domain layer instead of string |
| Missing vital defaults | HR→0, SBP→inf, SpO2→100 (safe defaults that don't trigger rules) |

---

### Documentation Update

**README.md Updated:**
Added "Adding New Inference Strategy" section with:
- Step 1: Create new strategy class extending BaseInference
- Step 2: Register strategy in InferenceFactory (static or dynamic)
- Step 3: Use the new strategy via InferenceService

**Status:** Phase 3C completed

---

# Phase 3 Post-Merge: Refactoring

## session_3_merge_1

**Date: 2026-01-11**

### Merge Conflict Resolution

**Context:**
Phase 3A, 3B, 3C branches merged to main. Conflicts in documentation files.

**Conflict Files:**
| File | Resolution |
|------|------------|
| `claude_works/DIALOG.md` | Keep 3A, 3B content + add 3C |
| `claude_works/vital_monitor/GLOBAL.md` | Mark 3A, 3B, 3C all as Completed |

**Analysis: Why main.py had no conflict:**
- Phase 3C branched from `47f8782` (Phase 2: Superseded)
- 3C added `inference_router` at different location (near `/health` endpoint)
- 3A/3B changes were at top of file (imports, routers, handlers)
- Git 3-way merge auto-resolved due to non-overlapping changes

---

## session_3_merge_2

**Date: 2026-01-11**

### XP-based Refactoring Analysis

**Objective:**
Analyze merged codebase for cleanup needs following XP principles.

**Initial Analysis (Before XP Review):**

| Issue | Priority |
|-------|----------|
| `schemas/__init__.py` incomplete exports | HIGH |
| `application/__init__.py` incomplete exports | HIGH |
| `main.py` scattered router registration | MEDIUM |
| `vital_router.py` no prefix pattern | MEDIUM |

**XP Principle Application:**

| Principle | Decision |
|-----------|----------|
| **YAGNI** | `__init__.py` export 추가 불필요 (사용처 0건) |
| **DRY** | `vital_router`에서 `/api/v1` 반복 제거 필요 |
| **Simple Design** | `main.py` 코드 그룹화 필요 |

**Final Refactoring Scope (XP Filtered):**

| Task | Do? | Reason |
|------|-----|--------|
| `main.py` 정리 | YES | Simple Design |
| `vital_router` prefix 적용 | YES | DRY |
| `__init__.py` export 추가 | NO | YAGNI (사용처 0건) |

---

## session_3_merge_3

**Date: 2026-01-11**

### Refactoring Execution

**Changes Made:**

1. **main.py** - Code organization
   - Grouped all router registrations together
   - Grouped all exception handlers together
   - Added section comments

2. **vital_router.py** - Prefix pattern
   - Changed: `APIRouter(tags=["vitals"])` → `APIRouter(prefix="/api/v1/vitals", tags=["vitals"])`
   - Removed `/api/v1/vitals` from each route decorator
   - Changed GET path: `/api/v1/patients/{patient_id}/vitals` → `/api/v1/vitals/patient/{patient_id}`

3. **test_vital_api.py** - Updated GET endpoint paths

4. **tests/e2e/conftest.py** - Deleted (was shadowing root conftest fixtures)

**Issue Found & Fixed:**
- `tests/e2e/conftest.py` (Phase 3C) was overriding `test_client` fixture
- This caused vital/patient API tests to fail (404 errors)
- Solution: Delete e2e conftest, use root conftest

**Test Results:**
```
61 passed
Coverage: 86.11%
```

---

## session_3_merge_4

**Date: 2026-01-11**

### Conftest Structure Improvement

**User Feedback:**
`test_client` is only used in e2e tests, should be in `tests/e2e/conftest.py`.

**Analysis:**

| Fixture | Unit Tests | E2E Tests |
|---------|------------|-----------|
| `test_engine` | Indirect (via db_session) | Indirect |
| `db_session` | Used (17 places) | Used |
| `test_client` | Not used | Used |

**Final Structure:**

```
tests/
├── conftest.py          # test_engine, db_session (shared)
└── e2e/
    ├── conftest.py      # test_client (e2e only)
    └── *.py
```

**Test Results:**
```
61 passed
Coverage: 86.11%
```

---

## session_3_merge_5

**Date: 2026-01-11**

### API Version Management Strategy

**User Question:**
How to structure for future v2 API? Concerns about file separation vs confusion.

**Options Documented in README:**

| Option | Structure | Pros | Cons |
|--------|-----------|------|------|
| **A** | `api/v1/`, `api/v2/` directories | Clear separation | File relocation needed |
| **B** | `v1.py`, `v2.py` + shared `routers/` | Minimal changes, reusable routers | Less clear separation |

**Decision:** Document both options in README for future reference (YAGNI - not implementing now)

**README Updated:**
Added "Future: API Version Management" section with Option A and B details.

**Status:** Phase 3 post-merge refactoring completed

# Vital Monitor API - Global Plan

## Project Goal

Build a Hospital Vital Signs Monitoring REST API with:
- Doctor authentication (JWT + argon2 + AES-256)
- Patient management with optimistic locking
- Vital data CRUD with optimistic locking
- Rule-based risk inference (pluggable strategy pattern)
- Docker containerization with auto-migration

## Tech Stack

| Component | Choice |
|-----------|--------|
| Language | Python 3.13 |
| Framework | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy (async) |
| Auth | Static Bearer Token (server-to-server) |
| Migration | Alembic |
| Package Manager | uv |
| Testing | pytest + pytest-cov |

## Project Structure

```
src/app/
├── main.py
├── config.py
├── dependencies.py          # Bearer token validation
├── domain/
│   ├── patient.py
│   ├── vital.py
│   ├── vital_type.py
│   ├── risk_level.py
│   ├── exceptions.py
│   └── inference/
│       ├── base.py
│       ├── rule_based_inference.py
│       └── factory.py
├── application/
│   ├── patient_service.py
│   ├── vital_service.py
│   └── inference_service.py
├── infrastructure/
│   ├── database.py
│   ├── models/
│   │   ├── base.py
│   │   ├── patient_model.py
│   │   └── vital_model.py
│   └── repositories/
└── presentation/
    ├── patient_router.py
    ├── vital_router.py
    ├── inference_router.py
    └── schemas/
```

## Phase Overview

| Phase | Name | Dependencies | Status |
|-------|------|--------------|--------|
| 0.5 | Environment Setup | - | **Completed** |
| 1 | Database Foundation | 0.5 | **Completed** |
| 2 | Authentication (JWT) | 1 | ~~Superseded~~ |
| 2.5 | Auth Migration (Bearer Token) | 2 | **Completed** |
| 3A | Patient API | 2.5 | **Completed** |
| 3B | Vital Data API | 2.5 | **Completed** |
| 3C | Inference API | 2.5 | **Completed** |
| 4 | Containerization | All | Pending |
| 5 | CI Pipeline | 0.5 | Pending |

## Common Guidelines

### Database Conventions
- All datetime stored in **UTC**
- `created_at`: Auto UTCNOW on INSERT (server_default)
- `updated_at`: Auto UTCNOW on INSERT/UPDATE (server_default + onupdate)
- Use `TIMESTAMPTZ` for all datetime columns

### Optimistic Locking Pattern
```python
stmt = update(Model).where(
    Model.id == id,
    Model.version == expected_version
).values(
    ...,
    version=Model.version + 1
).returning(Model)

if result is None:
    raise OptimisticLockError  # -> 409 Conflict
```

### Authentication (Post Phase 2.5)
- Static Bearer token configured in `.env`
- Simple token comparison (no JWT complexity)
- Server-to-server communication model

### Error Handling
- OptimisticLockError -> 409 Conflict
- PatientNotFoundError -> 404 Not Found
- InvalidTokenError -> 401 Unauthorized
- SessionExpiredError -> 401 Unauthorized

### Testing
- Target coverage: >= 75%
- Test DB: `vital_monitor_test`
- Suite start: `alembic upgrade head`
- Suite end: `alembic downgrade base`
- Each test: transaction rollback for isolation
- API tests: Direct HTTP calls via TestClient (no mocking)
- Time-related tests: Use past timestamps (iat/exp = now - 5min) or DB manipulation (access_token_expires_at = now - 1hour)

## References

- Spec: `claude_works/spec.md`
- Dialog History: `claude_works/PHASE_0_DIALOG.md`
- Python Guidelines: `claude_works/claude_py.md`

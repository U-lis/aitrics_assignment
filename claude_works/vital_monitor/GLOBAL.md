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
| Auth | JWT + argon2 (password) + AES-256 (token storage) |
| Migration | Alembic |
| Package Manager | uv |
| Testing | pytest + pytest-cov |

## Project Structure

```
src/app/
├── main.py
├── config.py
├── dependencies.py
├── domain/
│   ├── patient.py
│   ├── vital.py
│   ├── doctor.py
│   ├── vital_type.py
│   ├── risk_level.py
│   ├── exceptions.py
│   └── inference/
│       ├── base.py
│       ├── rule_based_inference.py
│       └── factory.py
├── application/
│   ├── auth_service.py
│   ├── patient_service.py
│   ├── vital_service.py
│   └── inference_service.py
├── infrastructure/
│   ├── database.py
│   ├── models/
│   │   ├── base.py
│   │   ├── doctor_model.py
│   │   ├── patient_model.py
│   │   └── vital_model.py
│   ├── repositories/
│   └── auth/
│       ├── jwt_handler.py
│       ├── password_handler.py
│       └── token_encryption.py
└── presentation/
    ├── router.py
    ├── auth_router.py
    ├── patient_router.py
    ├── vital_router.py
    ├── inference_router.py
    └── schemas/
```

## Phase Overview

| Phase | Name | Dependencies | Status |
|-------|------|--------------|--------|
| 0.5 | Environment Setup | - | Pending |
| 1 | Database Foundation | 0.5 | Pending |
| 2 | Authentication | 1 | Pending |
| 3A | Patient API | 2 | Pending |
| 3B | Vital Data API | 2 | Pending |
| 3C | Inference API | 2 | Pending |
| 4 | Containerization | All | Pending |

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

### Token Expiration (Critical)
| Concept | Duration | Purpose |
|---------|----------|---------|
| `access_token_expires_at` (DB) | 1 hour | Token reuse period |
| JWT `exp` field | 3 min | JWT signature validation only |

### Error Handling
- OptimisticLockError -> 409 Conflict
- PatientNotFoundError -> 404 Not Found
- InvalidTokenError -> 401 Unauthorized
- SessionExpiredError -> 401 Unauthorized

### Testing (TBD)
- Test cases to be discussed and added to each phase file
- Target coverage: >= 75%

## References

- Spec: `claude_works/spec.md`
- Dialog History: `claude_works/PHASE_0_DIALOG.md`
- Python Guidelines: `claude_works/claude_py.md`

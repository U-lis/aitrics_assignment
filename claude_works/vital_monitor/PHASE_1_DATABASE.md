# Phase 1: Database Foundation

## Objective

Establish database connectivity, ORM models, and migration infrastructure.

## Tasks

### 1. Create src/app/config.py

Use pydantic-settings with dotenv:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    AES_SECRET_KEY: str

    class Config:
        env_file = ".env"
```

### 2. Create src/app/infrastructure/database.py

Async SQLAlchemy setup:
- `create_async_engine` with DATABASE_URL
- `async_sessionmaker` for session factory
- `get_db_session` async generator for DI

### 3. Create Base Model (src/app/infrastructure/models/base.py)

```python
from sqlalchemy import Column, DateTime, func
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
```

### 4. Create ORM Models

#### DoctorModel (src/app/infrastructure/models/doctor_model.py)

| Column | Type | Notes |
|--------|------|-------|
| id | VARCHAR(50) | PK |
| password_hash | VARCHAR(255) | argon2 |
| name | VARCHAR(100) | |
| access_token | TEXT | AES-256 encrypted |
| refresh_token | TEXT | AES-256 encrypted |
| access_token_expires_at | TIMESTAMPTZ | nullable |

Properties:
- `decrypted_access_token`
- `decrypted_refresh_token`
- `set_tokens(access_token, refresh_token, expires_at)`
- `is_access_token_valid()`

#### PatientModel (src/app/infrastructure/models/patient_model.py)

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK, default gen_random_uuid() |
| patient_id | VARCHAR(20) | UNIQUE, INDEX |
| name | VARCHAR(100) | |
| gender | CHAR(1) | CHECK M/F |
| birth_date | DATE | |
| version | INTEGER | default 1 |

#### VitalModel (src/app/infrastructure/models/vital_model.py)

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| patient_id | VARCHAR(20) | FK -> patients, INDEX |
| recorded_at | TIMESTAMPTZ | INDEX |
| vital_type | VARCHAR(10) | CHECK enum |
| value | DECIMAL(10,2) | |
| version | INTEGER | default 1 |

### 5. Create Domain Entities

- `src/app/domain/doctor.py`
- `src/app/domain/patient.py`
- `src/app/domain/vital.py`
- `src/app/domain/vital_type.py` (Enum: HR, RR, SBP, DBP, SpO2, BT)
- `src/app/domain/risk_level.py` (Enum: LOW, MEDIUM, HIGH)
- `src/app/domain/exceptions.py`

### 6. Initialize Alembic

```bash
uv run alembic init alembic
```

Configure `alembic/env.py` for async PostgreSQL.

### 7. Create Initial Migration

```bash
uv run alembic revision --autogenerate -m "Initial tables"
uv run alembic upgrade head
```

### 8. Create Repository Interfaces

- `src/app/infrastructure/repositories/doctor_repository.py`
- `src/app/infrastructure/repositories/patient_repository.py`
- `src/app/infrastructure/repositories/vital_repository.py`

## Checklist

- [ ] config.py created with Settings class
- [ ] database.py created with async engine
- [ ] Base model with TimestampMixin created
- [ ] DoctorModel with properties created
- [ ] PatientModel created
- [ ] VitalModel created
- [ ] Domain entities created
- [ ] Domain enums created
- [ ] Domain exceptions created
- [ ] Alembic initialized
- [ ] Initial migration created and applied
- [ ] Repository interfaces created

## Test Cases

### Migration Tests (tests/unit/test_migrations.py)

| Test | Description |
|------|-------------|
| test_migration_upgrade_head | alembic upgrade head succeeds |
| test_migration_tables_exist | All tables created (doctors, patients, vitals) |

### Model Tests (tests/unit/test_models.py)

| Test | Description |
|------|-------------|
| test_doctor_model_create | Create and query Doctor |
| test_doctor_model_set_tokens | set_tokens() stores encrypted tokens |
| test_doctor_model_decrypted_properties | decrypted_access_token, decrypted_refresh_token work |
| test_doctor_model_is_access_token_valid_true | Valid within expires_at |
| test_doctor_model_is_access_token_valid_false | Invalid after expires_at |
| test_patient_model_create | Create Patient (version=1) |
| test_patient_model_auto_timestamps | created_at, updated_at auto-generated |
| test_vital_model_create | Create Vital with FK |
| test_vital_model_patient_fk_constraint | FK violation raises error |

### Repository Tests (tests/unit/test_repositories.py)

| Test | Description |
|------|-------------|
| test_doctor_repo_find_by_id | Find Doctor by ID |
| test_doctor_repo_find_by_id_not_found | Return None for missing ID |
| test_patient_repo_find_by_patient_id | Find Patient by patient_id |
| test_patient_repo_exists | Check patient_id exists |
| test_vital_repo_find_by_time_range | Query by time range |
| test_vital_repo_find_by_time_range_with_type | Filter by vital_type |

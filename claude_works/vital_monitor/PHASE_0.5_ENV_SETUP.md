# Phase 0.5: Environment Setup

## Objective

Set up development environment with all required dependencies and configuration files.

## Tasks

### 1. Update pyproject.toml

Add the following dependencies:

```toml
[project]
dependencies = [
    "fastapi[standard]>=0.115.0",
    "sqlalchemy[asyncio]>=2.0.0",
    "asyncpg>=0.30.0",
    "alembic>=1.14.0",
    "pydantic-settings>=2.0.0",
    "python-jose[cryptography]>=3.3.0",
    "python-dotenv>=1.0.0",
    "argon2-cffi>=23.1.0",
    "pycryptodome>=3.20.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "pytest-cov>=6.0.0",
    "httpx>=0.28.0",
]
```

### 2. Create .env.example

```
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/vital_monitor

# JWT
JWT_SECRET_KEY=your-jwt-secret-key-here
JWT_ALGORITHM=HS256

# AES-256 Encryption (32 bytes = 256 bits)
AES_SECRET_KEY=your-32-byte-aes-secret-key-here
```

### 3. Create pytest.ini or pyproject.toml pytest config

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
addopts = "-v --cov=src/app --cov-report=term-missing"
```

### 4. Create basic project structure

Create empty `__init__.py` files:
- `src/__init__.py`
- `src/app/__init__.py`
- `src/app/domain/__init__.py`
- `src/app/application/__init__.py`
- `src/app/infrastructure/__init__.py`
- `src/app/presentation/__init__.py`
- `tests/__init__.py`

### 5. Run uv sync

```bash
uv sync
uv sync --dev
```

## Checklist

- [ ] pyproject.toml updated with all dependencies
- [ ] .env.example created
- [ ] pytest configuration added
- [ ] Basic directory structure created
- [ ] uv sync successful

## Test Cases (TBD)

To be discussed with user.

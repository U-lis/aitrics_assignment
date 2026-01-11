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
    "ruff>=0.8.0",
    "ty>=0.0.1a0",
    "pre-commit>=4.0.0",
    "ipython>=8.0.0",
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
addopts = "-v --cov=src/app --cov-report=term-missing --cov-fail-under=75"
```

### 4. Add ruff configuration to pyproject.toml

```toml
[tool.ruff]
line-length = 120
target-version = "py313"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]

[tool.ruff.format]
quote-style = "double"
```

### 5. Add ty configuration to pyproject.toml

```toml
[tool.ty]
python-version = "3.13"
```

### 6. Create .pre-commit-config.yaml

```yaml
repos:
  - repo: local
    hooks:
      - id: ruff-lint
        name: ruff lint
        entry: uv run ruff check --fix
        language: system
        types: [python]
        stages: [pre-commit]

      - id: ruff-format
        name: ruff format
        entry: uv run ruff format
        language: system
        types: [python]
        stages: [pre-commit]

      - id: pytest
        name: pytest
        entry: uv run pytest
        language: system
        types: [python]
        stages: [pre-push]
        pass_filenames: false
```

### 7. Create basic project structure

Create empty `__init__.py` files:
- `src/__init__.py`
- `src/app/__init__.py`
- `src/app/domain/__init__.py`
- `src/app/application/__init__.py`
- `src/app/infrastructure/__init__.py`
- `src/app/presentation/__init__.py`
- `tests/__init__.py`

### 8. Run uv sync

```bash
uv sync
uv sync --dev
```

### 9. Install pre-commit hooks

```bash
uv run pre-commit install
uv run pre-commit install --hook-type pre-push
```

### 10. Update README.md

Add "How to use" section with:
- Instructions to copy `.env.example` to `.env`
- Database URL configuration guide
- JWT secret key generation example (`secrets.token_urlsafe(32)`)
- AES-256 secret key generation example (`os.urandom(32)` + base64 encode)
- Dependency installation command (`uv sync --all-extras`)
- Pre-commit hooks setup commands

## Checklist

- [x] pyproject.toml updated with all dependencies
- [x] .env.example created
- [x] pytest configuration added
- [x] ruff configuration added
- [x] ty configuration added
- [x] .pre-commit-config.yaml created
- [x] Basic directory structure created
- [x] uv sync successful
- [x] pre-commit hooks installed
- [x] coverage threshold (75%) configured
- [x] README.md updated with setup instructions

## Test Setup

### Add to .env.example
```
TEST_DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/vital_monitor_test
```

### Create tests/conftest.py

```python
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from fastapi.testclient import TestClient
from alembic.config import Config
from alembic import command

TEST_DB_URL = "postgresql+asyncpg://user:pass@localhost:5432/vital_monitor_test"

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Session-scoped: alembic upgrade/downgrade"""
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", TEST_DB_URL.replace("+asyncpg", ""))

    # Upgrade at start
    command.upgrade(alembic_cfg, "head")
    yield
    # Downgrade at end
    command.downgrade(alembic_cfg, "base")

@pytest.fixture
async def db_session():
    """Function-scoped: transaction rollback after each test"""
    engine = create_async_engine(TEST_DB_URL)
    async with engine.connect() as conn:
        trans = await conn.begin()
        session = AsyncSession(bind=conn)
        yield session
        await trans.rollback()
    await engine.dispose()

@pytest.fixture
def client(db_session):
    """FastAPI TestClient with DB override"""
    from src.app.main import app
    from src.app.dependencies import get_db_session

    app.dependency_overrides[get_db_session] = lambda: db_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
def auth_client(client):
    """TestClient with valid auth token"""
    client.post("/auth/register", json={
        "id": "test_doctor",
        "password": "test_password",
        "name": "Test Doctor"
    })
    response = client.post("/auth/login", json={
        "id": "test_doctor",
        "password": "test_password"
    })
    token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client
```

### Test Directory Structure

```
tests/
├── __init__.py
├── conftest.py
├── unit/
│   └── __init__.py
└── e2e/
    └── __init__.py
```

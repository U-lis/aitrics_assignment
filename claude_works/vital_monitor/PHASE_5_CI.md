# Phase 5: CI Pipeline

## Objective

Set up GitHub Actions CI pipeline to automatically validate code quality on every push and pull request.

## Dependencies

- Phase 0.5 (Environment Setup) - dev dependencies must be defined

## Requirements

1. Run ruff for linting and format checking
2. Run ty for type checking
3. Run pytest with PostgreSQL for integration tests
4. Upload coverage report to Codecov
5. Trigger on all branches (push and PR)

## Tasks

### 1. Ensure Dev Dependencies in pyproject.toml

Verify the following are in `[project.optional-dependencies]` dev section:

```toml
[project.optional-dependencies]
dev = [
    "ruff>=0.8.0",
    "ty>=0.0.1a6",
    "pytest>=8.0",
    "pytest-asyncio>=0.24",
    "pytest-cov>=6.0",
    "httpx>=0.27",
]
```

If not present, add them.

### 2. Create GitHub Actions Workflow

Location: `.github/workflows/ci.yml`

Create directory structure first: `.github/workflows/`

```yaml
name: CI

on:
  push:
  pull_request:

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up uv
        uses: astral-sh/setup-uv@v5

      - name: Install dependencies
        run: uv sync --frozen --dev

      - name: Ruff check
        run: uv run ruff check .

      - name: Ruff format check
        run: uv run ruff format --check .

  typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up uv
        uses: astral-sh/setup-uv@v5

      - name: Install dependencies
        run: uv sync --frozen --dev

      - name: Type check with ty
        run: uv run ty check src/

  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: vital_monitor_test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    env:
      DATABASE_URL: postgresql+asyncpg://test:test@localhost:5432/vital_monitor_test
      JWT_SECRET_KEY: test-jwt-secret-key-for-ci
      AES_SECRET_KEY: test-aes-32-byte-secret-key!!
    steps:
      - uses: actions/checkout@v4

      - name: Set up uv
        uses: astral-sh/setup-uv@v5

      - name: Install dependencies
        run: uv sync --frozen --dev

      - name: Run migrations
        run: uv run alembic upgrade head

      - name: Run tests with coverage
        run: uv run pytest --cov=src --cov-report=xml

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          files: coverage.xml
        continue-on-error: true
```

### 3. Verify Tool Configurations in pyproject.toml

Ensure the following tool configurations exist:

```toml
[tool.ruff]
target-version = "py313"
line-length = 120

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]

[tool.ruff.format]
quote-style = "double"

[tool.ty]
python-version = "3.13"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

## Checklist

- [x] Dev dependencies verified/added to pyproject.toml
- [x] `.github/workflows/` directory created
- [x] `ci.yml` workflow file created
- [x] Tool configurations verified in pyproject.toml
- [x] Local verification: `uv run ruff check .`
- [x] Local verification: `uv run ruff format --check .`
- [x] Local verification: `uv run ty check src/`
- [x] Local verification: `uv run pytest`
- [ ] Push to GitHub and verify Actions run successfully

## Verification

### Local Verification

```bash
# Lint check
uv run ruff check .

# Format check
uv run ruff format --check .

# Type check
uv run ty check src/

# Run tests
uv run pytest --cov=src
```

### GitHub Verification

1. Push code to any branch or create a PR
2. Navigate to repository's Actions tab
3. Verify all 3 jobs (lint, typecheck, test) pass
4. Check Codecov for coverage report (if configured)

## Notes

- `ty` is Astral's new type checker (alternative to mypy/pyright), still in alpha
- All 3 jobs run in parallel for faster CI feedback
- PostgreSQL service container is used for integration tests
- Codecov upload has `continue-on-error: true` to prevent CI failure if upload fails
- AES_SECRET_KEY must be exactly 32 bytes for AES-256

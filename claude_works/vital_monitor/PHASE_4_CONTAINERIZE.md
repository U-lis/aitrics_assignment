# Phase 4: Containerization

## Objective

Docker setup with auto-migration and external access.

## Requirements

1. Auto-run `alembic upgrade head` on service startup
2. External access via `localhost:8080`

## Tasks

### 1. Create Dockerfile

Location: `Dockerfile`

```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen

# Copy application code
COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Copy entrypoint script
COPY entrypoint.sh ./
RUN chmod +x entrypoint.sh

# Expose port
EXPOSE 8000

# Run entrypoint
ENTRYPOINT ["./entrypoint.sh"]
```

### 2. Create entrypoint.sh

Location: `entrypoint.sh`

```bash
#!/bin/bash
set -e

echo "Running database migrations..."
uv run alembic upgrade head

echo "Starting application..."
exec uv run uvicorn src.app.main:app --host 0.0.0.0 --port 8000
```

### 3. Create docker-compose.yml

Location: `docker-compose.yml`

```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: aitrics
      POSTGRES_PASSWORD: aitrics
      POSTGRES_DB: vital_monitor
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U aitrics"]
      interval: 5s
      timeout: 5s
      retries: 5

  api:
    build: .
    ports:
      - "8080:8000"  # External access via localhost:8080
    environment:
      - DATABASE_URL=postgresql+asyncpg://aitrics:aitrics@db:5432/vital_monitor
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - AES_SECRET_KEY=${AES_SECRET_KEY}
    depends_on:
      db:
        condition: service_healthy

volumes:
  postgres_data:
```

### 4. Create .dockerignore

Location: `.dockerignore`

```
.git
.gitignore
.env
.venv
__pycache__
*.pyc
*.pyo
.pytest_cache
.coverage
htmlcov
*.egg-info
dist
build
claude_works
*.md
!README.md
```

### 5. Update README.md

Add sections:
- Quick Start with docker-compose
- API Documentation (Swagger URL)
- Environment Variables
- Optimistic Lock explanation

### 6. Finalize .env.example

Ensure all required variables are documented:
```
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/vital_monitor
JWT_SECRET_KEY=your-jwt-secret-key-here
JWT_ALGORITHM=HS256
AES_SECRET_KEY=your-32-byte-aes-secret-key-here
```

## Usage

```bash
# Start services
docker-compose up --build

# Access API
# Swagger UI: http://localhost:8080/docs
# OpenAPI JSON: http://localhost:8080/openapi.json

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## Checklist

- [ ] Dockerfile created
- [ ] entrypoint.sh created with alembic migration
- [ ] docker-compose.yml created
- [ ] .dockerignore created
- [ ] README.md updated
- [ ] .env.example finalized
- [ ] Container builds successfully
- [ ] Migrations run automatically on startup
- [ ] API accessible at localhost:8080
- [ ] Swagger UI accessible at localhost:8080/docs

## Test Cases (TBD)

To be discussed with user.

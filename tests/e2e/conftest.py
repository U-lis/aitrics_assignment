import os
from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# Set env vars before importing app
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://user:password@localhost:5432/vital_monitor")
os.environ.setdefault("TEST_DATABASE_URL", "postgresql+asyncpg://user:password@localhost:5432/vital_monitor_test")
os.environ.setdefault("BEARER_TOKEN", "test-bearer-token")

from app.config import get_settings  # noqa: E402
from app.main import app  # noqa: E402

# Clear settings cache to ensure test token is used
get_settings.cache_clear()


@pytest_asyncio.fixture
async def test_client() -> AsyncGenerator[AsyncClient]:
    """Create test client without database dependency."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

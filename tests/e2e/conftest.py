from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.infrastructure.database import get_db_session
from app.main import app


@pytest_asyncio.fixture
async def test_client(test_engine) -> AsyncGenerator[AsyncClient]:
    """Create test client with overridden database dependency."""
    async_session_factory = async_sessionmaker(test_engine, expire_on_commit=False)

    async def override_get_db_session() -> AsyncGenerator[AsyncSession]:
        async with async_session_factory() as session:
            yield session
            await session.commit()

    app.dependency_overrides[get_db_session] = override_get_db_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()

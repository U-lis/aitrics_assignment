import os
from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Set test BEARER_TOKEN before importing settings
os.environ.setdefault("BEARER_TOKEN", "test-bearer-token")

from app.config import get_settings
from app.infrastructure.database import get_db_session
from app.infrastructure.models import Base
from app.main import app

settings = get_settings()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(settings.TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession]:
    async_session_factory = async_sessionmaker(test_engine, expire_on_commit=False)
    async with async_session_factory() as session:
        yield session
        await session.rollback()


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

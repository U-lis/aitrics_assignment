from collections.abc import AsyncGenerator

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings
from app.infrastructure.models import Base

settings = get_settings()


@pytest_asyncio.fixture
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

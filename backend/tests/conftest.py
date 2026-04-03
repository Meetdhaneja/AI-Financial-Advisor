from collections.abc import AsyncGenerator
import os
import sys
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ["REDIS_URL"] = "redis://localhost:6379/15"

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.cache import cache
from app.db.base import Base
from app.db.init_db import init_db
from app.db.session import get_db_session
from app.main import create_application



@pytest_asyncio.fixture()
async def client() -> AsyncGenerator[AsyncClient, None]:
    engine = create_async_engine(
        TEST_DATABASE_URL,
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

    app = create_application(use_lifespan=False)

    async def override_db() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db_session] = override_db

    async with session_factory() as session:
        await init_db(session, db_engine=engine)

    await cache.connect()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as test_client:
        yield test_client
    await cache.disconnect()
    await engine.dispose()

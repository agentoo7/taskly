"""Pytest configuration and fixtures for testing."""

import asyncio
from collections.abc import AsyncGenerator
import os

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.database import Base
from app.main import app
from app.models import *  # noqa: F401, F403

# Test database URL (use a separate test database)
# Use 'postgres' hostname when running inside Docker, 'localhost' when running locally
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://taskly:taskly@localhost:5432/taskly_test"
)


# Configure pytest-asyncio to use function scope by default
pytest_plugins = ('pytest_asyncio',)


@pytest.fixture(scope="function")
def event_loop():
    """Create an event loop for each test function."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session(event_loop):
    """Create a fresh database session for each test (sync wrapper for async fixture)."""
    async def _create_session() -> AsyncGenerator[AsyncSession, None]:
        # Create engine with NullPool to avoid connection pool issues
        test_engine = create_async_engine(
            TEST_DATABASE_URL,
            echo=False,
            poolclass=NullPool,
        )

        TestSessionLocal = async_sessionmaker(
            test_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        # Create all tables
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        # Create and yield session
        async with TestSessionLocal() as session:
            yield session
            await session.rollback()

        # Drop all tables after test
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

        # Dispose of engine
        await test_engine.dispose()

    # Run async generator and return session
    gen = _create_session()
    session = event_loop.run_until_complete(gen.__anext__())
    yield session
    # Cleanup
    try:
        event_loop.run_until_complete(gen.__anext__())
    except StopAsyncIteration:
        pass


@pytest.fixture(scope="function")
def client(db_session, event_loop):
    """Create an async HTTP client for testing the FastAPI app (sync wrapper)."""
    from app.core.database import get_db

    async def _create_client() -> AsyncGenerator[AsyncClient, None]:
        # Override database dependency to use test database
        async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
            yield db_session

        app.dependency_overrides[get_db] = override_get_db

        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac

        # Clear dependency overrides after test
        app.dependency_overrides.clear()

    # Run async generator and return client
    gen = _create_client()
    client_instance = event_loop.run_until_complete(gen.__anext__())
    yield client_instance
    # Cleanup
    try:
        event_loop.run_until_complete(gen.__anext__())
    except StopAsyncIteration:
        pass

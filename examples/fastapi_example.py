"""
FastAPI Integration Example

This example shows how to use pytest-green-light with FastAPI and SQLAlchemy async.

Note: This is an example file, not a test file. To use it:
1. Install dependencies: pip install fastapi pytest-asyncio aiosqlite
2. Copy the patterns into your own test files
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import Mapped, declarative_base, mapped_column

from pytest_green_light.fixtures import (
    async_db_transaction,
    async_engine_factory,
    async_session_factory,
)

# Base for SQLAlchemy models
Base = declarative_base()


# Example model
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str]


# FastAPI app
app = FastAPI()


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    """Example endpoint - in real app, would use dependency injection for session."""
    # This is just an example structure
    return {"user_id": user_id}


# Pytest fixtures
@pytest.fixture
async def engine():
    """Create async engine for testing."""
    async for eng in async_engine_factory("sqlite+aiosqlite:///:memory:"):
        # Create tables
        async with eng.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        yield eng


@pytest.fixture
async def session(engine: AsyncEngine):
    """Create async session for testing."""
    async for sess in async_session_factory(engine):
        yield sess


@pytest.fixture
async def client(engine: AsyncEngine):
    """Create FastAPI test client."""
    # In a real app, you'd override the database dependency
    return TestClient(app)


# Tests
pytestmark = pytest.mark.asyncio


async def test_create_user(session: AsyncSession):
    """Test creating a user with automatic rollback."""
    async with async_db_transaction(session):
        user = User(id=1, name="Alice", email="alice@example.com")
        session.add(user)
        await session.commit()

        # Verify user was created
        result = await session.get(User, 1)
        assert result is not None
        assert result.name == "Alice"

    # After transaction, user should be rolled back
    result = await session.get(User, 1)
    assert result is None


async def test_multiple_users(session: AsyncSession):
    """Test creating multiple users."""
    async with async_db_transaction(session):
        users = [
            User(id=1, name="Alice", email="alice@example.com"),
            User(id=2, name="Bob", email="bob@example.com"),
        ]
        for user in users:
            session.add(user)
        await session.commit()

        # Verify users exist
        result1 = await session.get(User, 1)
        result2 = await session.get(User, 2)
        assert result1 is not None
        assert result2 is not None


async def test_user_query(session: AsyncSession):
    """Test querying users."""
    async with async_db_transaction(session):
        # Create test data
        user = User(id=1, name="Alice", email="alice@example.com")
        session.add(user)
        await session.commit()

        # Query users
        from sqlalchemy import select

        stmt = select(User).where(User.name == "Alice")
        result = await session.execute(stmt)
        users = result.scalars().all()

        assert len(users) == 1
        assert users[0].name == "Alice"


async def test_nested_transaction(session: AsyncSession):
    """Test nested transactions (savepoints)."""
    # Create initial user
    async with async_db_transaction(session, rollback=False):
        user1 = User(id=1, name="Alice", email="alice@example.com")
        session.add(user1)
        await session.commit()

    # Nested transaction
    async with async_db_transaction(session, nested=True, rollback=True):
        user2 = User(id=2, name="Bob", email="bob@example.com")
        session.add(user2)
        await session.commit()

        # Both should exist during nested transaction
        result1 = await session.get(User, 1)
        result2 = await session.get(User, 2)
        assert result1 is not None
        assert result2 is not None

    # After nested transaction rollback, only first should exist
    result1 = await session.get(User, 1)
    result2 = await session.get(User, 2)
    assert result1 is not None
    assert result2 is None

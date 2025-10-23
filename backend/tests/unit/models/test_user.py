"""Unit tests for User model."""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


@pytest.mark.asyncio
async def test_user_creation(db_session: AsyncSession) -> None:
    """Test User model creation and basic attributes."""
    user = User(
        github_id=12345,
        username="testuser",
        email="test@example.com",
        avatar_url="https://example.com/avatar.png",
        github_access_token="fake_token",
    )

    db_session.add(user)
    await db_session.flush()

    assert user.id is not None
    assert isinstance(user.id, uuid.UUID)
    assert user.github_id == 12345
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.avatar_url == "https://example.com/avatar.png"
    assert user.created_at is not None
    assert user.updated_at is not None


@pytest.mark.asyncio
async def test_user_unique_github_id(db_session: AsyncSession) -> None:
    """Test that github_id must be unique."""
    user1 = User(
        github_id=12345,
        username="user1",
        email="user1@example.com",
    )
    user2 = User(
        github_id=12345,  # Duplicate github_id
        username="user2",
        email="user2@example.com",
    )

    db_session.add(user1)
    await db_session.flush()

    db_session.add(user2)
    with pytest.raises(Exception):  # Should raise IntegrityError
        await db_session.flush()


@pytest.mark.asyncio
async def test_user_repr(db_session: AsyncSession) -> None:
    """Test User __repr__ method."""
    user = User(
        github_id=12345,
        username="testuser",
        email="test@example.com",
    )

    db_session.add(user)
    await db_session.flush()

    assert "testuser" in repr(user)
    assert str(user.id) in repr(user)

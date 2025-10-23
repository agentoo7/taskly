"""Unit tests for Workspace model."""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.workspace import Workspace


@pytest.mark.asyncio
async def test_workspace_creation(db_session: AsyncSession) -> None:
    """Test Workspace model creation and basic attributes."""
    user = User(
        github_id=12345,
        username="testuser",
        email="test@example.com",
    )
    db_session.add(user)
    await db_session.flush()

    workspace = Workspace(
        name="Test Workspace",
        created_by=user.id,
    )
    db_session.add(workspace)
    await db_session.flush()

    assert workspace.id is not None
    assert isinstance(workspace.id, uuid.UUID)
    assert workspace.name == "Test Workspace"
    assert workspace.created_by == user.id
    assert workspace.created_at is not None
    assert workspace.updated_at is not None


@pytest.mark.asyncio
async def test_workspace_creator_relationship(db_session: AsyncSession) -> None:
    """Test Workspace creator relationship."""
    user = User(
        github_id=12345,
        username="testuser",
        email="test@example.com",
    )
    db_session.add(user)
    await db_session.flush()

    workspace = Workspace(
        name="Test Workspace",
        created_by=user.id,
    )
    db_session.add(workspace)
    await db_session.flush()
    await db_session.refresh(workspace, ["creator"])

    assert workspace.creator is not None
    assert workspace.creator.id == user.id
    assert workspace.creator.username == "testuser"

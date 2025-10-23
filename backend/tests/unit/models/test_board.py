"""Unit tests for Board model."""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.board import Board
from app.models.user import User
from app.models.workspace import Workspace


@pytest.mark.asyncio
async def test_board_creation_with_jsonb_columns(db_session: AsyncSession) -> None:
    """Test Board model creation with JSONB columns."""
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

    columns_data = [
        {"id": str(uuid.uuid4()), "name": "To Do", "position": 0},
        {"id": str(uuid.uuid4()), "name": "In Progress", "position": 1},
        {"id": str(uuid.uuid4()), "name": "Done", "position": 2},
    ]

    board = Board(
        workspace_id=workspace.id,
        name="Test Board",
        columns=columns_data,
        archived=False,
    )
    db_session.add(board)
    await db_session.flush()

    assert board.id is not None
    assert board.name == "Test Board"
    assert board.columns == columns_data
    assert board.archived is False
    assert len(board.columns) == 3
    assert board.columns[0]["name"] == "To Do"


@pytest.mark.asyncio
async def test_board_workspace_relationship(db_session: AsyncSession) -> None:
    """Test Board workspace relationship."""
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

    board = Board(
        workspace_id=workspace.id,
        name="Test Board",
        columns=[],
    )
    db_session.add(board)
    await db_session.flush()
    await db_session.refresh(board, ["workspace"])

    assert board.workspace is not None
    assert board.workspace.id == workspace.id
    assert board.workspace.name == "Test Workspace"

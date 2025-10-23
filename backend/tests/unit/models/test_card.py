"""Unit tests for Card model."""

import uuid
from datetime import date

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.board import Board
from app.models.card import Card, PriorityEnum
from app.models.user import User
from app.models.workspace import Workspace


@pytest.mark.asyncio
async def test_card_creation_with_enum_and_metadata(db_session: AsyncSession) -> None:
    """Test Card model creation with enums and JSONB metadata."""
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
        columns=[{"id": str(uuid.uuid4()), "name": "To Do", "position": 0}],
    )
    db_session.add(board)
    await db_session.flush()

    metadata = {
        "labels": [
            {"id": str(uuid.uuid4()), "name": "bug", "color": "red"},
            {"id": str(uuid.uuid4()), "name": "feature", "color": "blue"},
        ],
        "acceptance_criteria": "Must pass all tests",
    }

    card = Card(
        board_id=board.id,
        column_id=uuid.UUID(board.columns[0]["id"]),
        title="Test Card",
        description="This is a test card",
        card_metadata=metadata,
        priority=PriorityEnum.HIGH,
        story_points=5,
        due_date=date(2025, 12, 31),
        position=0,
        created_by=user.id,
    )
    db_session.add(card)
    await db_session.flush()

    assert card.id is not None
    assert card.title == "Test Card"
    assert card.priority == PriorityEnum.HIGH
    assert card.story_points == 5
    assert card.card_metadata == metadata
    assert len(card.card_metadata["labels"]) == 2
    assert card.position == 0


@pytest.mark.asyncio
async def test_card_priority_enum_values(db_session: AsyncSession) -> None:
    """Test Card priority enum values."""
    assert PriorityEnum.NONE == "none"
    assert PriorityEnum.LOW == "low"
    assert PriorityEnum.MEDIUM == "medium"
    assert PriorityEnum.HIGH == "high"
    assert PriorityEnum.URGENT == "urgent"


@pytest.mark.asyncio
async def test_card_board_relationship(db_session: AsyncSession) -> None:
    """Test Card board relationship."""
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
        columns=[{"id": str(uuid.uuid4()), "name": "To Do", "position": 0}],
    )
    db_session.add(board)
    await db_session.flush()

    card = Card(
        board_id=board.id,
        column_id=uuid.UUID(board.columns[0]["id"]),
        title="Test Card",
        created_by=user.id,
    )
    db_session.add(card)
    await db_session.flush()
    await db_session.refresh(card, ["board"])

    assert card.board is not None
    assert card.board.id == board.id
    assert card.board.name == "Test Board"

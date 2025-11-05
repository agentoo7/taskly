"""Unit tests for activity service."""

import pytest
from uuid import uuid4

from app.models.card_activity import ActivityAction
from app.services.activity_service import ActivityService


@pytest.fixture
def activity_service(db_session):
    """Create activity service instance."""
    return ActivityService(db_session)


@pytest.mark.asyncio
async def test_log_card_moved(activity_service, db_session):
    """Test logging card moved activity."""
    from app.models.card import Card
    from app.models.user import User
    from app.models.board import Board
    from app.models.workspace import Workspace

    # Create test data
    workspace = Workspace(name="Test Workspace")
    db_session.add(workspace)
    await db_session.flush()

    user = User(github_id=12345, username="testuser", email="test@example.com")
    db_session.add(user)
    await db_session.flush()

    board = Board(name="Test Board", workspace_id=workspace.id)
    db_session.add(board)
    await db_session.flush()

    card = Card(
        title="Test Card",
        board_id=board.id,
        column_id=uuid4(),
        created_by=user.id,
        position=0,
    )
    db_session.add(card)
    await db_session.flush()

    # Log activity
    activity = await activity_service.log_card_moved(
        card_id=card.id, user_id=user.id, from_column="To Do", to_column="In Progress"
    )

    assert activity.card_id == card.id
    assert activity.user_id == user.id
    assert activity.action == ActivityAction.MOVED
    assert activity.activity_metadata["from_column"] == "To Do"
    assert activity.activity_metadata["to_column"] == "In Progress"
    assert activity.to_description() == "moved from To Do to In Progress"


@pytest.mark.asyncio
async def test_log_user_assigned(activity_service, db_session):
    """Test logging user assignment activity."""
    from app.models.card import Card
    from app.models.user import User
    from app.models.board import Board
    from app.models.workspace import Workspace

    # Create test data
    workspace = Workspace(name="Test Workspace")
    db_session.add(workspace)
    await db_session.flush()

    user = User(github_id=12345, username="testuser", email="test@example.com")
    db_session.add(user)
    await db_session.flush()

    board = Board(name="Test Board", workspace_id=workspace.id)
    db_session.add(board)
    await db_session.flush()

    card = Card(
        title="Test Card",
        board_id=board.id,
        column_id=uuid4(),
        created_by=user.id,
        position=0,
    )
    db_session.add(card)
    await db_session.flush()

    # Log activity
    activity = await activity_service.log_user_assigned(
        card_id=card.id, user_id=user.id, assignee_name="Alice"
    )

    assert activity.action == ActivityAction.ASSIGNED
    assert activity.activity_metadata["assignee_name"] == "Alice"
    assert activity.to_description() == "assigned to Alice"


@pytest.mark.asyncio
async def test_log_priority_changed(activity_service, db_session):
    """Test logging priority change activity."""
    from app.models.card import Card
    from app.models.user import User
    from app.models.board import Board
    from app.models.workspace import Workspace

    # Create test data
    workspace = Workspace(name="Test Workspace")
    db_session.add(workspace)
    await db_session.flush()

    user = User(github_id=12345, username="testuser", email="test@example.com")
    db_session.add(user)
    await db_session.flush()

    board = Board(name="Test Board", workspace_id=workspace.id)
    db_session.add(board)
    await db_session.flush()

    card = Card(
        title="Test Card",
        board_id=board.id,
        column_id=uuid4(),
        created_by=user.id,
        position=0,
    )
    db_session.add(card)
    await db_session.flush()

    # Log activity
    activity = await activity_service.log_priority_changed(
        card_id=card.id, user_id=user.id, old_priority="low", new_priority="high"
    )

    assert activity.action == ActivityAction.PRIORITY_CHANGED
    assert activity.activity_metadata["old_priority"] == "low"
    assert activity.activity_metadata["new_priority"] == "high"
    assert activity.to_description() == "changed priority from low to high"

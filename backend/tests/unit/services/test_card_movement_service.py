"""Unit tests for CardMovementService."""

import uuid

import pytest
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.board import Board
from app.models.card import Card
from app.models.card_activity import CardActivity
from app.models.user import User
from app.models.workspace import Workspace
from app.models.workspace_member import RoleEnum, WorkspaceMember
from app.services.card_movement_service import CardMovementService


@pytest.fixture
async def movement_service(db_session: AsyncSession) -> CardMovementService:
    """Card movement service instance with test database."""
    return CardMovementService(db_session)


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Test user for card operations."""
    user = User(
        github_id=12345,
        username="testuser",
        email="test@example.com",
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.fixture
async def test_workspace(db_session: AsyncSession, test_user: User) -> Workspace:
    """Workspace for testing."""
    workspace = Workspace(
        name="Test Workspace",
        created_by=test_user.id,
    )
    db_session.add(workspace)
    await db_session.flush()

    # Add user as workspace member
    membership = WorkspaceMember(
        user_id=test_user.id,
        workspace_id=workspace.id,
        role=RoleEnum.MEMBER,
    )
    db_session.add(membership)
    await db_session.flush()

    return workspace


@pytest.fixture
async def test_board(db_session: AsyncSession, test_workspace: Workspace) -> Board:
    """Test board with columns."""
    board = Board(
        workspace_id=test_workspace.id,
        name="Test Board",
        columns=[
            {"id": str(uuid.uuid4()), "name": "To Do", "position": 0},
            {"id": str(uuid.uuid4()), "name": "In Progress", "position": 1},
            {"id": str(uuid.uuid4()), "name": "Done", "position": 2},
        ],
        archived=False,
    )
    db_session.add(board)
    await db_session.flush()
    return board


@pytest.mark.asyncio
async def test_move_card_within_same_column_down(
    movement_service: CardMovementService,
    test_board: Board,
    test_user: User,
    db_session: AsyncSession,
) -> None:
    """Test moving card down within same column (position 0 -> 2)."""
    col_id = uuid.UUID(test_board.columns[0]["id"])

    # Create 4 cards in column
    card0 = Card(
        board_id=test_board.id,
        column_id=col_id,
        title="Card 0",
        position=0,
    )
    card1 = Card(
        board_id=test_board.id,
        column_id=col_id,
        title="Card 1",
        position=1,
    )
    card2 = Card(
        board_id=test_board.id,
        column_id=col_id,
        title="Card 2",
        position=2,
    )
    card3 = Card(
        board_id=test_board.id,
        column_id=col_id,
        title="Card 3",
        position=3,
    )
    db_session.add_all([card0, card1, card2, card3])
    await db_session.flush()

    # Move card0 from position 0 to position 2
    await movement_service.move_card(
        card_id=card0.id,
        target_column_id=col_id,
        target_position=2,
        moved_by=test_user.id,
    )

    await db_session.commit()

    # Refresh cards
    await db_session.refresh(card0)
    await db_session.refresh(card1)
    await db_session.refresh(card2)
    await db_session.refresh(card3)

    # Card0 should now be at position 2
    assert card0.position == 2
    # Cards 1 and 2 should shift up
    assert card1.position == 0
    assert card2.position == 1
    # Card 3 stays at same position
    assert card3.position == 3


@pytest.mark.asyncio
async def test_move_card_within_same_column_up(
    movement_service: CardMovementService,
    test_board: Board,
    test_user: User,
    db_session: AsyncSession,
) -> None:
    """Test moving card up within same column (position 2 -> 0)."""
    col_id = uuid.UUID(test_board.columns[0]["id"])

    # Create 3 cards
    card0 = Card(
        board_id=test_board.id, column_id=col_id, title="Card 0", position=0
    )
    card1 = Card(
        board_id=test_board.id, column_id=col_id, title="Card 1", position=1
    )
    card2 = Card(
        board_id=test_board.id, column_id=col_id, title="Card 2", position=2
    )
    db_session.add_all([card0, card1, card2])
    await db_session.flush()

    # Move card2 from position 2 to position 0
    await movement_service.move_card(
        card_id=card2.id,
        target_column_id=col_id,
        target_position=0,
        moved_by=test_user.id,
    )

    await db_session.commit()
    await db_session.refresh(card0)
    await db_session.refresh(card1)
    await db_session.refresh(card2)

    # Card2 should now be at position 0
    assert card2.position == 0
    # Cards 0 and 1 should shift down
    assert card0.position == 1
    assert card1.position == 2


@pytest.mark.asyncio
async def test_move_card_between_columns(
    movement_service: CardMovementService,
    test_board: Board,
    test_user: User,
    db_session: AsyncSession,
) -> None:
    """Test moving card from one column to another."""
    col_a_id = uuid.UUID(test_board.columns[0]["id"])
    col_b_id = uuid.UUID(test_board.columns[1]["id"])

    # Create cards in column A
    card_a0 = Card(
        board_id=test_board.id, column_id=col_a_id, title="Card A0", position=0
    )
    card_a1 = Card(
        board_id=test_board.id, column_id=col_a_id, title="Card A1", position=1
    )
    card_a2 = Card(
        board_id=test_board.id, column_id=col_a_id, title="Card A2", position=2
    )

    # Create cards in column B
    card_b0 = Card(
        board_id=test_board.id, column_id=col_b_id, title="Card B0", position=0
    )
    card_b1 = Card(
        board_id=test_board.id, column_id=col_b_id, title="Card B1", position=1
    )

    db_session.add_all([card_a0, card_a1, card_a2, card_b0, card_b1])
    await db_session.flush()

    # Move card_a1 from column A position 1 to column B position 0
    await movement_service.move_card(
        card_id=card_a1.id,
        target_column_id=col_b_id,
        target_position=0,
        moved_by=test_user.id,
    )

    await db_session.commit()

    # Refresh all cards
    await db_session.refresh(card_a0)
    await db_session.refresh(card_a1)
    await db_session.refresh(card_a2)
    await db_session.refresh(card_b0)
    await db_session.refresh(card_b1)

    # Card A1 should now be in column B at position 0
    assert card_a1.column_id == col_b_id
    assert card_a1.position == 0

    # Remaining cards in column A should shift up
    assert card_a0.position == 0
    assert card_a2.position == 1  # Was position 2, shifts to 1

    # Cards in column B should shift down
    assert card_b0.position == 1  # Was position 0, shifts to 1
    assert card_b1.position == 2  # Was position 1, shifts to 2


@pytest.mark.asyncio
async def test_move_card_creates_activity_log(
    movement_service: CardMovementService,
    test_board: Board,
    test_user: User,
    db_session: AsyncSession,
) -> None:
    """Test that moving card creates activity log entry."""
    col_a_id = uuid.UUID(test_board.columns[0]["id"])
    col_b_id = uuid.UUID(test_board.columns[1]["id"])

    card = Card(
        board_id=test_board.id, column_id=col_a_id, title="Test Card", position=0
    )
    db_session.add(card)
    await db_session.flush()

    await movement_service.move_card(
        card_id=card.id,
        target_column_id=col_b_id,
        target_position=0,
        moved_by=test_user.id,
    )

    await db_session.commit()

    # Check activity log
    result = await db_session.execute(
        select(CardActivity).where(CardActivity.card_id == card.id)
    )
    activities = result.scalars().all()

    assert len(activities) == 1
    activity = activities[0]
    assert activity.action == "moved"
    assert activity.user_id == test_user.id
    assert activity.activity_metadata["from_column"] == str(col_a_id)
    assert activity.activity_metadata["to_column"] == str(col_b_id)
    assert activity.activity_metadata["from_position"] == 0
    assert activity.activity_metadata["to_position"] == 0
    assert "from_column_name" in activity.activity_metadata
    assert "to_column_name" in activity.activity_metadata


@pytest.mark.asyncio
async def test_move_card_to_archived_board_fails(
    movement_service: CardMovementService,
    test_board: Board,
    test_user: User,
    db_session: AsyncSession,
) -> None:
    """Test that moving card in archived board raises error."""
    # Archive the board
    test_board.archived = True
    await db_session.flush()

    col_id = uuid.UUID(test_board.columns[0]["id"])
    card = Card(
        board_id=test_board.id, column_id=col_id, title="Test Card", position=0
    )
    db_session.add(card)
    await db_session.flush()

    with pytest.raises(HTTPException) as exc_info:
        await movement_service.move_card(
            card_id=card.id,
            target_column_id=col_id,
            target_position=1,
            moved_by=test_user.id,
        )

    assert exc_info.value.status_code == 400
    assert "archived" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_move_card_to_invalid_column_fails(
    movement_service: CardMovementService,
    test_board: Board,
    test_user: User,
    db_session: AsyncSession,
) -> None:
    """Test that moving card to non-existent column raises error."""
    col_id = uuid.UUID(test_board.columns[0]["id"])
    card = Card(
        board_id=test_board.id, column_id=col_id, title="Test Card", position=0
    )
    db_session.add(card)
    await db_session.flush()

    invalid_column_id = uuid.uuid4()

    with pytest.raises(HTTPException) as exc_info:
        await movement_service.move_card(
            card_id=card.id,
            target_column_id=invalid_column_id,
            target_position=0,
            moved_by=test_user.id,
        )

    assert exc_info.value.status_code == 400
    assert "column" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_move_nonexistent_card_fails(
    movement_service: CardMovementService,
    test_board: Board,
    test_user: User,
    db_session: AsyncSession,
) -> None:
    """Test that moving non-existent card raises error."""
    col_id = uuid.UUID(test_board.columns[0]["id"])
    fake_card_id = uuid.uuid4()

    with pytest.raises(HTTPException) as exc_info:
        await movement_service.move_card(
            card_id=fake_card_id,
            target_column_id=col_id,
            target_position=0,
            moved_by=test_user.id,
        )

    assert exc_info.value.status_code == 404
    assert "card" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_bulk_move_cards(
    movement_service: CardMovementService,
    test_board: Board,
    test_user: User,
    db_session: AsyncSession,
) -> None:
    """Test bulk moving multiple cards to new column."""
    col_a_id = uuid.UUID(test_board.columns[0]["id"])
    col_b_id = uuid.UUID(test_board.columns[1]["id"])

    # Create cards in column A
    card1 = Card(
        board_id=test_board.id, column_id=col_a_id, title="Card 1", position=0
    )
    card2 = Card(
        board_id=test_board.id, column_id=col_a_id, title="Card 2", position=1
    )
    card3 = Card(
        board_id=test_board.id, column_id=col_a_id, title="Card 3", position=2
    )
    db_session.add_all([card1, card2, card3])
    await db_session.flush()

    # Bulk move card1 and card3 to column B
    await movement_service.bulk_move_cards(
        card_ids=[card1.id, card3.id],
        target_column_id=col_b_id,
        target_position=0,
        moved_by=test_user.id,
    )

    await db_session.commit()
    await db_session.refresh(card1)
    await db_session.refresh(card2)
    await db_session.refresh(card3)

    # Card1 and Card3 should be in column B at consecutive positions
    assert card1.column_id == col_b_id
    assert card1.position == 0
    assert card3.column_id == col_b_id
    assert card3.position == 1

    # Card2 should remain in column A, shifted up
    assert card2.column_id == col_a_id
    assert card2.position == 0  # Shifted up from position 1

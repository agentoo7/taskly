"""Unit tests for CardService."""

from datetime import date
import uuid
import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.board import Board
from app.models.card import Card, PriorityEnum
from app.models.user import User
from app.models.workspace import Workspace
from app.models.workspace_member import RoleEnum, WorkspaceMember
from app.services.card_service import CardService


@pytest.fixture
async def card_service(db_session: AsyncSession) -> CardService:
    """Card service instance with test database."""
    return CardService(db_session)


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
async def test_board(
    db_session: AsyncSession, test_workspace: Workspace
) -> Board:
    """Test board with columns."""
    board = Board(
        workspace_id=test_workspace.id,
        name="Test Board",
        columns=[
            {"id": str(uuid.uuid4()), "name": "To Do", "position": 0},
            {"id": str(uuid.uuid4()), "name": "In Progress", "position": 1},
            {"id": str(uuid.uuid4()), "name": "Done", "position": 2},
        ],
    )
    db_session.add(board)
    await db_session.flush()
    return board


@pytest.mark.asyncio
async def test_create_card_at_position_zero(
    card_service: CardService,
    test_board: Board,
    test_user: User,
    db_session: AsyncSession,
):
    """Test creating card at position 0 and incrementing existing cards."""
    column_id = test_board.columns[0]["id"]

    # Create first card
    card1 = await card_service.create_card(
        board_id=test_board.id,
        column_id=column_id,
        title="Card 1",
        user_id=test_user.id,
    )
    assert card1.position == 0
    assert card1.title == "Card 1"
    assert card1.board_id == test_board.id
    assert str(card1.column_id) == column_id

    # Create second card - should be at position 0, first card incremented to 1
    card2 = await card_service.create_card(
        board_id=test_board.id,
        column_id=column_id,
        title="Card 2",
        user_id=test_user.id,
    )
    assert card2.position == 0

    await db_session.refresh(card1)
    assert card1.position == 1


@pytest.mark.asyncio
async def test_create_card_invalid_column(
    card_service: CardService,
    test_board: Board,
    test_user: User,
):
    """Test creating card with invalid column ID raises error."""
    with pytest.raises(HTTPException) as exc_info:
        await card_service.create_card(
            board_id=test_board.id,
            column_id="invalid-column-id",
            title="Test Card",
            user_id=test_user.id,
        )
    assert exc_info.value.status_code == 400
    assert "Column does not exist" in exc_info.value.detail


@pytest.mark.asyncio
async def test_create_card_unauthorized_user(
    card_service: CardService,
    test_board: Board,
    db_session: AsyncSession,
):
    """Test creating card as non-workspace member raises error."""
    # Create user not in workspace
    other_user = User(
        github_id=99999,
        username="otheruser",
        email="other@example.com",
    )
    db_session.add(other_user)
    await db_session.flush()

    column_id = test_board.columns[0]["id"]

    with pytest.raises(HTTPException) as exc_info:
        await card_service.create_card(
            board_id=test_board.id,
            column_id=column_id,
            title="Test Card",
            user_id=other_user.id,
        )
    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_update_card(
    card_service: CardService,
    test_board: Board,
    test_user: User,
    db_session: AsyncSession,
):
    """Test updating card fields."""
    column_id = test_board.columns[0]["id"]

    # Create card
    card = await card_service.create_card(
        board_id=test_board.id,
        column_id=column_id,
        title="Original Title",
        user_id=test_user.id,
    )

    # Update card
    updated_card = await card_service.update_card(
        card_id=card.id,
        user_id=test_user.id,
        updates={
            "title": "Updated Title",
            "description": "Test description",
            "priority": PriorityEnum.HIGH,
            "story_points": 5,
            "due_date": date(2025, 12, 31),
        },
    )

    assert updated_card.title == "Updated Title"
    assert updated_card.description == "Test description"
    assert updated_card.priority == PriorityEnum.HIGH
    assert updated_card.story_points == 5
    assert updated_card.due_date == date(2025, 12, 31)


@pytest.mark.asyncio
async def test_get_board_cards(
    card_service: CardService,
    test_board: Board,
    test_user: User,
):
    """Test fetching cards for board."""
    column1_id = test_board.columns[0]["id"]
    column2_id = test_board.columns[1]["id"]

    # Create cards in different columns
    await card_service.create_card(
        test_board.id, column1_id, "Card 1", test_user.id
    )
    await card_service.create_card(
        test_board.id, column1_id, "Card 2", test_user.id
    )
    await card_service.create_card(
        test_board.id, column2_id, "Card 3", test_user.id
    )

    # Get all cards
    all_cards = await card_service.get_board_cards(
        board_id=test_board.id, user_id=test_user.id
    )
    assert len(all_cards) == 3

    # Get cards by column
    column1_cards = await card_service.get_board_cards(
        board_id=test_board.id, user_id=test_user.id, column_id=column1_id
    )
    assert len(column1_cards) == 2


@pytest.mark.asyncio
async def test_delete_card_and_reorder(
    card_service: CardService,
    test_board: Board,
    test_user: User,
    db_session: AsyncSession,
):
    """Test deleting card and reordering remaining cards."""
    column_id = test_board.columns[0]["id"]

    # Create three cards
    card1 = await card_service.create_card(
        test_board.id, column_id, "Card 1", test_user.id
    )
    card2 = await card_service.create_card(
        test_board.id, column_id, "Card 2", test_user.id
    )
    card3 = await card_service.create_card(
        test_board.id, column_id, "Card 3", test_user.id
    )

    # Verify initial positions (newest at top)
    await db_session.refresh(card1)
    await db_session.refresh(card2)
    await db_session.refresh(card3)
    assert card3.position == 0
    assert card2.position == 1
    assert card1.position == 2

    # Delete middle card (card2)
    await card_service.delete_card(card_id=card2.id, user_id=test_user.id)

    # Verify remaining cards reordered
    await db_session.refresh(card1)
    await db_session.refresh(card3)
    assert card3.position == 0
    assert card1.position == 1

    # Verify card was deleted
    cards = await card_service.get_board_cards(
        board_id=test_board.id, user_id=test_user.id, column_id=column_id
    )
    assert len(cards) == 2
    assert card2.id not in [c.id for c in cards]


@pytest.mark.asyncio
async def test_get_card_by_id(
    card_service: CardService,
    test_board: Board,
    test_user: User,
):
    """Test fetching single card by ID."""
    column_id = test_board.columns[0]["id"]

    created_card = await card_service.create_card(
        test_board.id, column_id, "Test Card", test_user.id
    )

    fetched_card = await card_service.get_card_by_id(
        card_id=created_card.id, user_id=test_user.id
    )

    assert fetched_card.id == created_card.id
    assert fetched_card.title == "Test Card"


@pytest.mark.asyncio
async def test_get_card_not_found(
    card_service: CardService,
    test_user: User,
    db_session: AsyncSession,
):
    """Test fetching non-existent card raises error."""
    import uuid

    fake_id = uuid.uuid4()

    with pytest.raises(HTTPException) as exc_info:
        await card_service.get_card_by_id(card_id=fake_id, user_id=test_user.id)

    assert exc_info.value.status_code == 404
    assert "Card not found" in exc_info.value.detail

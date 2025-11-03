"""Integration tests for cards API endpoints."""

from datetime import date
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.board import Board
from app.models.card import PriorityEnum
from app.models.user import User
from app.models.workspace import Workspace
from app.models.workspace_member import RoleEnum, WorkspaceMember
from app.services.auth_service import AuthService


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        github_id=111111,
        username="testuser",
        email="testuser@example.com",
        github_access_token="encrypted_token_1",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_token(test_user: User, db_session: AsyncSession) -> str:
    """Generate JWT access token for test user."""
    auth_service = AuthService(db_session)
    tokens = await auth_service.generate_jwt_tokens(test_user)
    return tokens["access_token"]


@pytest.fixture
async def test_workspace(
    db_session: AsyncSession, test_user: User
) -> Workspace:
    """Create test workspace."""
    workspace = Workspace(
        name="Test Workspace",
        created_by=test_user.id,
    )
    db_session.add(workspace)
    await db_session.flush()

    # Add user as member
    membership = WorkspaceMember(
        user_id=test_user.id,
        workspace_id=workspace.id,
        role=RoleEnum.MEMBER,
    )
    db_session.add(membership)
    await db_session.commit()
    await db_session.refresh(workspace)
    return workspace


@pytest.fixture
async def test_board(
    db_session: AsyncSession, test_workspace: Workspace
) -> Board:
    """Create test board with columns."""
    board = Board(
        workspace_id=test_workspace.id,
        name="Test Board",
        columns=[
            {"id": "col-1", "name": "To Do", "position": 0},
            {"id": "col-2", "name": "In Progress", "position": 1},
            {"id": "col-3", "name": "Done", "position": 2},
        ],
    )
    db_session.add(board)
    await db_session.commit()
    await db_session.refresh(board)
    return board


@pytest.mark.asyncio
async def test_create_card(
    client: AsyncClient,
    test_board: Board,
    test_token: str,
):
    """Test creating a card via API."""
    column_id = test_board.columns[0]["id"]

    response = await client.post(
        f"/api/boards/{test_board.id}/cards",
        json={
            "title": "Test Card",
            "column_id": column_id,
            "board_id": str(test_board.id),
        },
        headers={"Authorization": f"Bearer {test_token}"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Card"
    assert data["column_id"] == column_id
    assert data["position"] == 0
    assert data["priority"] == "none"


@pytest.mark.asyncio
async def test_create_card_invalid_column(
    client: AsyncClient,
    test_board: Board,
    test_token: str,
):
    """Test creating card with invalid column returns 400."""
    response = await client.post(
        f"/api/boards/{test_board.id}/cards",
        json={
            "title": "Test Card",
            "column_id": "invalid-column",
            "board_id": str(test_board.id),
        },
        headers={"Authorization": f"Bearer {test_token}"},
    )

    assert response.status_code == 400
    assert "Column does not exist" in response.json()["detail"]


@pytest.mark.asyncio
async def test_list_board_cards(
    client: AsyncClient,
    test_board: Board,
    test_token: str,
):
    """Test listing all cards in a board."""
    column_id = test_board.columns[0]["id"]

    # Create multiple cards
    for i in range(3):
        await client.post(
            f"/api/boards/{test_board.id}/cards",
            json={
                "title": f"Card {i + 1}",
                "column_id": column_id,
                "board_id": str(test_board.id),
            },
            headers={"Authorization": f"Bearer {test_token}"},
        )

    # List all cards
    response = await client.get(
        f"/api/boards/{test_board.id}/cards",
        headers={"Authorization": f"Bearer {test_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["position"] == 0  # Newest at top


@pytest.mark.asyncio
async def test_filter_cards_by_column(
    client: AsyncClient,
    test_board: Board,
    test_token: str,
):
    """Test filtering cards by column."""
    col1_id = test_board.columns[0]["id"]
    col2_id = test_board.columns[1]["id"]

    # Create cards in different columns
    await client.post(
        f"/api/boards/{test_board.id}/cards",
        json={
            "title": "Card in Col 1",
            "column_id": col1_id,
            "board_id": str(test_board.id),
        },
        headers={"Authorization": f"Bearer {test_token}"},
    )
    await client.post(
        f"/api/boards/{test_board.id}/cards",
        json={
            "title": "Card in Col 2",
            "column_id": col2_id,
            "board_id": str(test_board.id),
        },
        headers={"Authorization": f"Bearer {test_token}"},
    )

    # Filter by column 1
    response = await client.get(
        f"/api/boards/{test_board.id}/cards?column_id={col1_id}",
        headers={"Authorization": f"Bearer {test_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["column_id"] == col1_id


@pytest.mark.asyncio
async def test_get_card_details(
    client: AsyncClient,
    test_board: Board,
    test_token: str,
):
    """Test getting card details."""
    column_id = test_board.columns[0]["id"]

    # Create card
    create_response = await client.post(
        f"/api/boards/{test_board.id}/cards",
        json={
            "title": "Test Card",
            "column_id": column_id,
            "board_id": str(test_board.id),
        },
        headers={"Authorization": f"Bearer {test_token}"},
    )
    card_id = create_response.json()["id"]

    # Get card details
    response = await client.get(
        f"/api/cards/{card_id}",
        headers={"Authorization": f"Bearer {test_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == card_id
    assert data["title"] == "Test Card"


@pytest.mark.asyncio
async def test_update_card(
    client: AsyncClient,
    test_board: Board,
    test_token: str,
):
    """Test updating card fields."""
    column_id = test_board.columns[0]["id"]

    # Create card
    create_response = await client.post(
        f"/api/boards/{test_board.id}/cards",
        json={
            "title": "Original Title",
            "column_id": column_id,
            "board_id": str(test_board.id),
        },
        headers={"Authorization": f"Bearer {test_token}"},
    )
    card_id = create_response.json()["id"]

    # Update card
    response = await client.patch(
        f"/api/cards/{card_id}",
        json={
            "title": "Updated Title",
            "description": "Test description",
            "priority": "high",
            "story_points": 5,
            "due_date": "2025-12-31",
        },
        headers={"Authorization": f"Bearer {test_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["description"] == "Test description"
    assert data["priority"] == "high"
    assert data["story_points"] == 5
    assert data["due_date"] == "2025-12-31"


@pytest.mark.asyncio
async def test_update_card_validation(
    client: AsyncClient,
    test_board: Board,
    test_token: str,
):
    """Test card update validation."""
    column_id = test_board.columns[0]["id"]

    # Create card
    create_response = await client.post(
        f"/api/boards/{test_board.id}/cards",
        json={
            "title": "Test Card",
            "column_id": column_id,
            "board_id": str(test_board.id),
        },
        headers={"Authorization": f"Bearer {test_token}"},
    )
    card_id = create_response.json()["id"]

    # Try invalid story points
    response = await client.patch(
        f"/api/cards/{card_id}",
        json={"story_points": 100},  # Max is 99
        headers={"Authorization": f"Bearer {test_token}"},
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_delete_card(
    client: AsyncClient,
    test_board: Board,
    test_token: str,
):
    """Test deleting a card."""
    column_id = test_board.columns[0]["id"]

    # Create card
    create_response = await client.post(
        f"/api/boards/{test_board.id}/cards",
        json={
            "title": "To Be Deleted",
            "column_id": column_id,
            "board_id": str(test_board.id),
        },
        headers={"Authorization": f"Bearer {test_token}"},
    )
    card_id = create_response.json()["id"]

    # Delete card
    response = await client.delete(
        f"/api/cards/{card_id}",
        headers={"Authorization": f"Bearer {test_token}"},
    )

    assert response.status_code == 204

    # Verify card is gone
    get_response = await client.get(
        f"/api/cards/{card_id}",
        headers={"Authorization": f"Bearer {test_token}"},
    )
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_card_reorders_positions(
    client: AsyncClient,
    test_board: Board,
    test_token: str,
):
    """Test that deleting a card reorders remaining cards."""
    column_id = test_board.columns[0]["id"]

    # Create three cards
    cards = []
    for i in range(3):
        response = await client.post(
            f"/api/boards/{test_board.id}/cards",
            json={
                "title": f"Card {i + 1}",
                "column_id": column_id,
                "board_id": str(test_board.id),
            },
            headers={"Authorization": f"Bearer {test_token}"},
        )
        cards.append(response.json())

    # Delete middle card
    await client.delete(
        f"/api/cards/{cards[1]['id']}",
        headers={"Authorization": f"Bearer {test_token}"},
    )

    # Check remaining cards have correct positions
    list_response = await client.get(
        f"/api/boards/{test_board.id}/cards?column_id={column_id}",
        headers={"Authorization": f"Bearer {test_token}"},
    )

    remaining_cards = list_response.json()
    assert len(remaining_cards) == 2
    assert remaining_cards[0]["position"] == 0
    assert remaining_cards[1]["position"] == 1


@pytest.mark.asyncio
async def test_unauthorized_access(
    client: AsyncClient,
    test_board: Board,
):
    """Test that unauthorized requests are rejected."""
    response = await client.get(f"/api/boards/{test_board.id}/cards")

    assert response.status_code == 401

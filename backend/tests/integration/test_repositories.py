"""Integration tests for repositories with real database."""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.board import Board
from app.models.card import Card, PriorityEnum
from app.models.user import User
from app.models.workspace import Workspace
from app.repositories.board_repository import BoardRepository
from app.repositories.card_repository import CardRepository
from app.repositories.user_repository import UserRepository
from app.repositories.workspace_repository import WorkspaceRepository


@pytest.mark.asyncio
async def test_user_repository_crud(db_session: AsyncSession) -> None:
    """Test UserRepository CRUD operations."""
    repo = UserRepository(db_session)

    # Create
    user = User(
        github_id=12345,
        username="testuser",
        email="test@example.com",
    )
    created_user = await repo.create(user)
    assert created_user.id is not None

    # Read by ID
    found_user = await repo.get_by_id(created_user.id)
    assert found_user is not None
    assert found_user.username == "testuser"

    # Read by GitHub ID
    found_by_github = await repo.get_by_github_id(12345)
    assert found_by_github is not None
    assert found_by_github.id == created_user.id

    # Read by email
    found_by_email = await repo.get_by_email("test@example.com")
    assert found_by_email is not None
    assert found_by_email.id == created_user.id

    # Update
    found_user.username = "updated_user"
    updated_user = await repo.update(found_user)
    assert updated_user.username == "updated_user"

    # Delete
    await repo.delete(found_user)
    await db_session.commit()

    deleted_user = await repo.get_by_id(created_user.id)
    assert deleted_user is None


@pytest.mark.asyncio
async def test_workspace_repository_crud(db_session: AsyncSession) -> None:
    """Test WorkspaceRepository CRUD operations."""
    user_repo = UserRepository(db_session)
    workspace_repo = WorkspaceRepository(db_session)

    # Create user first
    user = await user_repo.create(
        User(github_id=12345, username="testuser", email="test@example.com")
    )

    # Create workspace
    workspace = Workspace(name="Test Workspace", created_by=user.id)
    created_workspace = await workspace_repo.create(workspace)
    assert created_workspace.id is not None
    assert created_workspace.name == "Test Workspace"

    # Get by creator
    user_workspaces = await workspace_repo.get_by_creator(user.id)
    assert len(user_workspaces) == 1
    assert user_workspaces[0].name == "Test Workspace"


@pytest.mark.asyncio
async def test_board_repository_crud(db_session: AsyncSession) -> None:
    """Test BoardRepository CRUD operations."""
    user_repo = UserRepository(db_session)
    workspace_repo = WorkspaceRepository(db_session)
    board_repo = BoardRepository(db_session)

    # Create user and workspace
    user = await user_repo.create(
        User(github_id=12345, username="testuser", email="test@example.com")
    )
    workspace = await workspace_repo.create(Workspace(name="Test Workspace", created_by=user.id))

    # Create board
    board = Board(
        workspace_id=workspace.id,
        name="Test Board",
        columns=[{"id": str(uuid.uuid4()), "name": "To Do", "position": 0}],
    )
    created_board = await board_repo.create(board)
    assert created_board.id is not None

    # Get by workspace
    workspace_boards = await board_repo.get_by_workspace(workspace.id)
    assert len(workspace_boards) == 1
    assert workspace_boards[0].name == "Test Board"

    # Get active boards
    active_boards = await board_repo.get_active_by_workspace(workspace.id)
    assert len(active_boards) == 1

    # Archive board and test filter
    created_board.archived = True
    await board_repo.update(created_board)
    active_boards = await board_repo.get_active_by_workspace(workspace.id)
    assert len(active_boards) == 0


@pytest.mark.asyncio
async def test_card_repository_crud(db_session: AsyncSession) -> None:
    """Test CardRepository CRUD operations."""
    user_repo = UserRepository(db_session)
    workspace_repo = WorkspaceRepository(db_session)
    board_repo = BoardRepository(db_session)
    card_repo = CardRepository(db_session)

    # Create user, workspace, and board
    user = await user_repo.create(
        User(github_id=12345, username="testuser", email="test@example.com")
    )
    workspace = await workspace_repo.create(Workspace(name="Test Workspace", created_by=user.id))
    column_id = uuid.uuid4()
    board = await board_repo.create(
        Board(
            workspace_id=workspace.id,
            name="Test Board",
            columns=[{"id": str(column_id), "name": "To Do", "position": 0}],
        )
    )

    # Create card
    card = Card(
        board_id=board.id,
        column_id=column_id,
        title="Test Card",
        description="Test description",
        priority=PriorityEnum.HIGH,
        position=0,
        created_by=user.id,
    )
    created_card = await card_repo.create(card)
    assert created_card.id is not None
    assert created_card.title == "Test Card"

    # Get by board
    board_cards = await card_repo.get_by_board(board.id)
    assert len(board_cards) == 1

    # Get by column
    column_cards = await card_repo.get_by_column(board.id, column_id)
    assert len(column_cards) == 1

    # Get by creator
    user_cards = await card_repo.get_by_creator(user.id)
    assert len(user_cards) == 1


@pytest.mark.asyncio
async def test_repository_get_all(db_session: AsyncSession) -> None:
    """Test BaseRepository get_all with pagination."""
    repo = UserRepository(db_session)

    # Create multiple users
    for i in range(15):
        user = User(
            github_id=10000 + i,
            username=f"user{i}",
            email=f"user{i}@example.com",
        )
        await repo.create(user)

    # Get all with default pagination
    all_users = await repo.get_all()
    assert len(all_users) == 15

    # Get with custom pagination
    page_1 = await repo.get_all(skip=0, limit=5)
    assert len(page_1) == 5

    page_2 = await repo.get_all(skip=5, limit=5)
    assert len(page_2) == 5

    page_3 = await repo.get_all(skip=10, limit=5)
    assert len(page_3) == 5

"""Unit tests for BoardService."""

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.board import Board
from app.models.user import User
from app.models.workspace import Workspace
from app.models.workspace_member import RoleEnum, WorkspaceMember
from app.services.board_service import BoardService, BOARD_TEMPLATES


@pytest.fixture
async def board_service(db_session: AsyncSession) -> BoardService:
    """Board service instance with test database."""
    return BoardService(db_session)


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Test user for board operations."""
    user = User(
        github_id=12345,
        username="testuser",
        email="test@example.com",
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.fixture
async def test_admin(db_session: AsyncSession) -> User:
    """Admin user for workspace operations."""
    user = User(
        github_id=67890,
        username="adminuser",
        email="admin@example.com",
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.fixture
async def test_workspace(db_session: AsyncSession, test_admin: User) -> Workspace:
    """Workspace for testing."""
    workspace = Workspace(
        name="Test Workspace",
        created_by=test_admin.id,
    )
    db_session.add(workspace)
    await db_session.flush()

    # Add admin as workspace member
    membership = WorkspaceMember(
        user_id=test_admin.id,
        workspace_id=workspace.id,
        role=RoleEnum.ADMIN,
    )
    db_session.add(membership)
    await db_session.flush()

    return workspace


@pytest.fixture
async def test_board(
    db_session: AsyncSession, test_workspace: Workspace
) -> Board:
    """Test board with kanban template."""
    board = Board(
        workspace_id=test_workspace.id,
        name="Test Board",
        columns=BOARD_TEMPLATES["kanban"].copy(),
    )
    db_session.add(board)
    await db_session.flush()
    return board


@pytest.mark.asyncio
async def test_create_board_blank_template(
    board_service: BoardService,
    test_workspace: Workspace,
    test_admin: User,
    db_session: AsyncSession,
):
    """Test creating board with blank template."""
    board = await board_service.create_board(
        workspace_id=test_workspace.id,
        name="My Blank Board",
        user_id=test_admin.id,
        template="blank",
    )

    assert board.id is not None
    assert board.workspace_id == test_workspace.id
    assert board.name == "My Blank Board"
    assert board.columns == []
    assert board.archived is False


@pytest.mark.asyncio
async def test_create_board_kanban_template(
    board_service: BoardService,
    test_workspace: Workspace,
    test_admin: User,
    db_session: AsyncSession,
):
    """Test creating board with kanban template."""
    board = await board_service.create_board(
        workspace_id=test_workspace.id,
        name="My Kanban Board",
        user_id=test_admin.id,
        template="kanban",
    )

    assert board.id is not None
    assert len(board.columns) == 4
    assert board.columns[0]["name"] == "To Do"
    assert board.columns[0]["position"] == 0
    assert board.columns[3]["name"] == "Done"
    assert board.columns[3]["position"] == 3


@pytest.mark.asyncio
async def test_create_board_invalid_template(
    board_service: BoardService,
    test_workspace: Workspace,
    test_admin: User,
):
    """Test creating board with invalid template raises error."""
    with pytest.raises(HTTPException) as exc_info:
        await board_service.create_board(
            workspace_id=test_workspace.id,
            name="Invalid Board",
            user_id=test_admin.id,
            template="invalid_template",
        )

    assert exc_info.value.status_code == 400
    assert "Invalid template" in exc_info.value.detail


@pytest.mark.asyncio
async def test_create_board_not_workspace_member(
    board_service: BoardService,
    test_workspace: Workspace,
    test_user: User,
):
    """Test creating board fails if user not workspace member."""
    with pytest.raises(HTTPException) as exc_info:
        await board_service.create_board(
            workspace_id=test_workspace.id,
            name="Unauthorized Board",
            user_id=test_user.id,
            template="blank",
        )

    assert exc_info.value.status_code == 403
    assert "not a member" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_workspace_boards(
    board_service: BoardService,
    test_workspace: Workspace,
    test_admin: User,
    test_board: Board,
    db_session: AsyncSession,
):
    """Test getting all boards in workspace."""
    # Create another board
    board2 = Board(
        workspace_id=test_workspace.id,
        name="Second Board",
        columns=[],
    )
    db_session.add(board2)
    await db_session.flush()

    boards = await board_service.get_workspace_boards(
        workspace_id=test_workspace.id,
        user_id=test_admin.id,
        include_archived=False,
    )

    assert len(boards) == 2
    assert boards[0].id in [test_board.id, board2.id]


@pytest.mark.asyncio
async def test_get_workspace_boards_excludes_archived(
    board_service: BoardService,
    test_workspace: Workspace,
    test_admin: User,
    test_board: Board,
    db_session: AsyncSession,
):
    """Test archived boards excluded by default."""
    # Create archived board
    archived_board = Board(
        workspace_id=test_workspace.id,
        name="Archived Board",
        columns=[],
        archived=True,
    )
    db_session.add(archived_board)
    await db_session.flush()

    boards = await board_service.get_workspace_boards(
        workspace_id=test_workspace.id,
        user_id=test_admin.id,
        include_archived=False,
    )

    assert len(boards) == 1
    assert boards[0].id == test_board.id


@pytest.mark.asyncio
async def test_get_board_by_id(
    board_service: BoardService,
    test_board: Board,
    test_admin: User,
):
    """Test getting board by ID."""
    board = await board_service.get_board_by_id(
        board_id=test_board.id,
        user_id=test_admin.id,
    )

    assert board.id == test_board.id
    assert board.name == test_board.name


@pytest.mark.asyncio
async def test_get_board_not_found(
    board_service: BoardService,
    test_admin: User,
):
    """Test getting non-existent board raises 404."""
    from uuid import uuid4

    with pytest.raises(HTTPException) as exc_info:
        await board_service.get_board_by_id(
            board_id=uuid4(),
            user_id=test_admin.id,
        )

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_update_board_name(
    board_service: BoardService,
    test_board: Board,
    test_admin: User,
):
    """Test updating board name."""
    updated = await board_service.update_board(
        board_id=test_board.id,
        user_id=test_admin.id,
        name="Updated Name",
    )

    assert updated.name == "Updated Name"
    assert updated.id == test_board.id


@pytest.mark.asyncio
async def test_update_board_columns(
    board_service: BoardService,
    test_board: Board,
    test_admin: User,
):
    """Test updating board columns."""
    new_columns = [
        {"id": "col1", "name": "Backlog", "position": 0},
        {"id": "col2", "name": "Active", "position": 1},
    ]

    updated = await board_service.update_board(
        board_id=test_board.id,
        user_id=test_admin.id,
        columns=new_columns,
    )

    assert len(updated.columns) == 2
    assert updated.columns[0]["name"] == "Backlog"
    assert updated.columns[1]["position"] == 1


@pytest.mark.asyncio
async def test_update_board_invalid_columns(
    board_service: BoardService,
    test_board: Board,
    test_admin: User,
):
    """Test updating with invalid column structure raises error."""
    invalid_columns = [
        {"name": "Missing ID"},  # Missing 'id' field
    ]

    with pytest.raises(HTTPException) as exc_info:
        await board_service.update_board(
            board_id=test_board.id,
            user_id=test_admin.id,
            columns=invalid_columns,
        )

    assert exc_info.value.status_code == 400
    assert "Invalid column structure" in exc_info.value.detail


@pytest.mark.asyncio
async def test_update_board_archive_requires_admin(
    board_service: BoardService,
    test_board: Board,
    test_user: User,
    test_workspace: Workspace,
    db_session: AsyncSession,
):
    """Test archiving board requires admin permission."""
    # Add test_user as regular member
    membership = WorkspaceMember(
        user_id=test_user.id,
        workspace_id=test_workspace.id,
        role=RoleEnum.MEMBER,
    )
    db_session.add(membership)
    await db_session.flush()

    with pytest.raises(HTTPException) as exc_info:
        await board_service.update_board(
            board_id=test_board.id,
            user_id=test_user.id,
            archived=True,
        )

    assert exc_info.value.status_code == 403
    assert "admin" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_delete_board(
    board_service: BoardService,
    test_board: Board,
    test_admin: User,
    db_session: AsyncSession,
):
    """Test deleting board."""
    await board_service.delete_board(
        board_id=test_board.id,
        user_id=test_admin.id,
    )

    # Verify board deleted
    from sqlalchemy import select

    result = await db_session.execute(select(Board).where(Board.id == test_board.id))
    deleted_board = result.scalar_one_or_none()
    assert deleted_board is None


@pytest.mark.asyncio
async def test_delete_board_requires_admin(
    board_service: BoardService,
    test_board: Board,
    test_user: User,
    test_workspace: Workspace,
    db_session: AsyncSession,
):
    """Test deleting board requires admin permission."""
    # Add test_user as regular member
    membership = WorkspaceMember(
        user_id=test_user.id,
        workspace_id=test_workspace.id,
        role=RoleEnum.MEMBER,
    )
    db_session.add(membership)
    await db_session.flush()

    with pytest.raises(HTTPException) as exc_info:
        await board_service.delete_board(
            board_id=test_board.id,
            user_id=test_user.id,
        )

    assert exc_info.value.status_code == 403

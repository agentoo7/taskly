"""Unit tests for AssigneeService."""

import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.board import Board
from app.models.card import Card
from app.models.user import User
from app.models.workspace import Workspace
from app.models.workspace_member import RoleEnum, WorkspaceMember
from app.services.assignee_service import AssigneeService


@pytest.fixture
async def assignee_service(db_session: AsyncSession) -> AssigneeService:
    """Assignee service instance with test database."""
    return AssigneeService(db_session)


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Test user for assignee operations."""
    user = User(
        github_id=12345,
        username="testuser",
        email="test@example.com",
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.fixture
async def assignee_user(db_session: AsyncSession) -> User:
    """User to be assigned to cards."""
    user = User(
        github_id=54321,
        username="assigneeuser",
        email="assignee@example.com",
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.fixture
async def other_user(db_session: AsyncSession) -> User:
    """Another test user (not a workspace member)."""
    user = User(
        github_id=67890,
        username="otheruser",
        email="other@example.com",
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.fixture
async def test_workspace(
    db_session: AsyncSession, test_user: User, assignee_user: User
) -> Workspace:
    """Workspace for testing."""
    workspace = Workspace(
        name="Test Workspace",
        created_by=test_user.id,
    )
    db_session.add(workspace)
    await db_session.flush()

    # Add both users as workspace members
    membership1 = WorkspaceMember(
        user_id=test_user.id,
        workspace_id=workspace.id,
        role=RoleEnum.MEMBER,
    )
    membership2 = WorkspaceMember(
        user_id=assignee_user.id,
        workspace_id=workspace.id,
        role=RoleEnum.MEMBER,
    )
    db_session.add_all([membership1, membership2])
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
        ],
    )
    db_session.add(board)
    await db_session.flush()
    return board


@pytest.fixture
async def test_card(
    db_session: AsyncSession, test_board: Board
) -> Card:
    """Test card for assignee operations."""
    card = Card(
        board_id=test_board.id,
        column_id=uuid.UUID(test_board.columns[0]["id"]),
        title="Test Card",
        position=0,
    )
    db_session.add(card)
    await db_session.flush()
    return card


@pytest.mark.asyncio
async def test_assign_user_to_card(
    assignee_service: AssigneeService,
    test_card: Card,
    test_user: User,
    assignee_user: User,
):
    """Test assigning a user to a card."""
    result = await assignee_service.assign_user_to_card(
        card_id=test_card.id,
        user_id=assignee_user.id,
        current_user_id=test_user.id,
    )

    # Verify assignment was created
    assert result.id == assignee_user.id
    assert result.username == assignee_user.username


@pytest.mark.asyncio
async def test_assign_non_member_raises_error(
    assignee_service: AssigneeService,
    test_card: Card,
    test_user: User,
    other_user: User,
):
    """Test assigning a non-workspace-member raises ValueError."""
    with pytest.raises(ValueError, match="not a member"):
        await assignee_service.assign_user_to_card(
            card_id=test_card.id,
            user_id=other_user.id,
            current_user_id=test_user.id,
        )


@pytest.mark.asyncio
async def test_assign_by_non_member_raises_permission_error(
    assignee_service: AssigneeService,
    test_card: Card,
    assignee_user: User,
    other_user: User,
):
    """Test assigning by a non-workspace-member raises PermissionError."""
    with pytest.raises(PermissionError):
        await assignee_service.assign_user_to_card(
            card_id=test_card.id,
            user_id=assignee_user.id,
            current_user_id=other_user.id,
        )


@pytest.mark.asyncio
async def test_assign_duplicate_raises_error(
    assignee_service: AssigneeService,
    test_card: Card,
    test_user: User,
    assignee_user: User,
):
    """Test assigning same user twice raises ValueError."""
    # Assign first time
    await assignee_service.assign_user_to_card(
        card_id=test_card.id,
        user_id=assignee_user.id,
        current_user_id=test_user.id,
    )

    # Try to assign again - should raise ValueError
    with pytest.raises(ValueError, match="already assigned"):
        await assignee_service.assign_user_to_card(
            card_id=test_card.id,
            user_id=assignee_user.id,
            current_user_id=test_user.id,
        )


@pytest.mark.asyncio
async def test_unassign_user_from_card(
    assignee_service: AssigneeService,
    test_card: Card,
    test_user: User,
    assignee_user: User,
):
    """Test unassigning a user from a card."""
    # First assign the user
    await assignee_service.assign_user_to_card(
        card_id=test_card.id,
        user_id=assignee_user.id,
        current_user_id=test_user.id,
    )

    # Then unassign
    result = await assignee_service.unassign_user_from_card(
        card_id=test_card.id,
        user_id=assignee_user.id,
        current_user_id=test_user.id,
    )

    # Verify unassignment succeeded
    assert result is True


@pytest.mark.asyncio
async def test_unassign_by_non_member_raises_permission_error(
    assignee_service: AssigneeService,
    test_card: Card,
    test_user: User,
    assignee_user: User,
    other_user: User,
):
    """Test unassigning by a non-workspace-member raises PermissionError."""
    # First assign the user
    await assignee_service.assign_user_to_card(
        card_id=test_card.id,
        user_id=assignee_user.id,
        current_user_id=test_user.id,
    )

    # Try to unassign by non-member
    with pytest.raises(PermissionError):
        await assignee_service.unassign_user_from_card(
            card_id=test_card.id,
            user_id=assignee_user.id,
            current_user_id=other_user.id,
        )


@pytest.mark.asyncio
async def test_unassign_not_assigned_returns_false(
    assignee_service: AssigneeService,
    test_card: Card,
    test_user: User,
    assignee_user: User,
):
    """Test unassigning a user that's not assigned returns False."""
    result = await assignee_service.unassign_user_from_card(
        card_id=test_card.id,
        user_id=assignee_user.id,
        current_user_id=test_user.id,
    )
    assert result is False


@pytest.mark.asyncio
async def test_get_card_assignees(
    assignee_service: AssigneeService,
    test_card: Card,
    test_user: User,
    assignee_user: User,
    db_session: AsyncSession,
):
    """Test getting all assignees for a card."""
    # Assign multiple users
    await assignee_service.assign_user_to_card(
        card_id=test_card.id,
        user_id=test_user.id,
        current_user_id=test_user.id,
    )
    await assignee_service.assign_user_to_card(
        card_id=test_card.id,
        user_id=assignee_user.id,
        current_user_id=test_user.id,
    )

    # Get assignees using the repository method
    from app.repositories.assignee_repository import AssigneeRepository
    repo = AssigneeRepository(db_session)
    assignees = await repo.get_card_assignees(test_card.id)

    assert len(assignees) == 2
    assignee_ids = {a.id for a in assignees}
    assert test_user.id in assignee_ids
    assert assignee_user.id in assignee_ids


@pytest.mark.asyncio
async def test_is_user_assigned(
    assignee_service: AssigneeService,
    test_card: Card,
    test_user: User,
    assignee_user: User,
    db_session: AsyncSession,
):
    """Test checking if a user is assigned to a card."""
    from app.repositories.assignee_repository import AssigneeRepository
    repo = AssigneeRepository(db_session)

    # Before assignment
    is_assigned = await repo.is_user_assigned(
        card_id=test_card.id,
        user_id=assignee_user.id,
    )
    assert is_assigned is False

    # After assignment
    await assignee_service.assign_user_to_card(
        card_id=test_card.id,
        user_id=assignee_user.id,
        current_user_id=test_user.id,
    )

    is_assigned = await repo.is_user_assigned(
        card_id=test_card.id,
        user_id=assignee_user.id,
    )
    assert is_assigned is True

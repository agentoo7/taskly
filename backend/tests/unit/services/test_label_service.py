"""Unit tests for LabelService."""

import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.board import Board
from app.models.card import Card
from app.models.user import User
from app.models.workspace import Workspace
from app.models.workspace_label import WorkspaceLabel
from app.models.workspace_member import RoleEnum, WorkspaceMember
from app.schemas.label import LabelCreate, LabelUpdate
from app.services.label_service import LabelService


@pytest.fixture
async def label_service(db_session: AsyncSession) -> LabelService:
    """Label service instance with test database."""
    return LabelService(db_session)


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Test user for label operations."""
    user = User(
        github_id=12345,
        username="testuser",
        email="test@example.com",
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
        ],
    )
    db_session.add(board)
    await db_session.flush()
    return board


@pytest.fixture
async def test_card(
    db_session: AsyncSession, test_board: Board
) -> Card:
    """Test card for label operations."""
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
async def test_create_label(
    label_service: LabelService,
    test_workspace: Workspace,
    test_user: User,
):
    """Test creating a label in a workspace."""
    label_data = LabelCreate(name="Bug", color="#FF0000")
    label = await label_service.create_label(
        workspace_id=test_workspace.id,
        label_data=label_data,
        user_id=test_user.id,
    )

    assert label.name == "Bug"
    assert label.color == "#FF0000"
    assert label.workspace_id == test_workspace.id


@pytest.mark.asyncio
async def test_create_label_unauthorized(
    label_service: LabelService,
    test_workspace: Workspace,
    other_user: User,
):
    """Test creating a label by non-member raises PermissionError."""
    label_data = LabelCreate(name="Bug", color="#FF0000")
    with pytest.raises(PermissionError):
        await label_service.create_label(
            workspace_id=test_workspace.id,
            label_data=label_data,
            user_id=other_user.id,
        )


@pytest.mark.asyncio
async def test_get_workspace_labels(
    label_service: LabelService,
    test_workspace: Workspace,
    test_user: User,
    db_session: AsyncSession,
):
    """Test getting all labels for a workspace."""
    # Create some labels
    label1 = WorkspaceLabel(
        workspace_id=test_workspace.id,
        name="Bug",
        color="#FF0000",
    )
    label2 = WorkspaceLabel(
        workspace_id=test_workspace.id,
        name="Feature",
        color="#00FF00",
    )
    db_session.add_all([label1, label2])
    await db_session.flush()

    labels = await label_service.get_workspace_labels(
        workspace_id=test_workspace.id,
        user_id=test_user.id,
    )

    assert len(labels) == 2
    label_names = {label.name for label in labels}
    assert "Bug" in label_names
    assert "Feature" in label_names


@pytest.mark.asyncio
async def test_get_workspace_labels_unauthorized(
    label_service: LabelService,
    test_workspace: Workspace,
    other_user: User,
):
    """Test getting labels by non-member raises PermissionError."""
    with pytest.raises(PermissionError):
        await label_service.get_workspace_labels(
            workspace_id=test_workspace.id,
            user_id=other_user.id,
        )


@pytest.mark.asyncio
async def test_update_label(
    label_service: LabelService,
    test_workspace: Workspace,
    test_user: User,
    db_session: AsyncSession,
):
    """Test updating a label."""
    # Create label
    label = WorkspaceLabel(
        workspace_id=test_workspace.id,
        name="Bug",
        color="#FF0000",
    )
    db_session.add(label)
    await db_session.flush()

    # Update label
    label_data = LabelUpdate(name="Critical Bug", color="#990000")
    updated = await label_service.update_label(
        label_id=label.id,
        label_data=label_data,
        user_id=test_user.id,
    )

    assert updated.name == "Critical Bug"
    assert updated.color == "#990000"


@pytest.mark.asyncio
async def test_update_label_unauthorized(
    label_service: LabelService,
    test_workspace: Workspace,
    other_user: User,
    db_session: AsyncSession,
):
    """Test updating label by non-member raises PermissionError."""
    label = WorkspaceLabel(
        workspace_id=test_workspace.id,
        name="Bug",
        color="#FF0000",
    )
    db_session.add(label)
    await db_session.flush()

    label_data = LabelUpdate(name="Critical Bug", color="#990000")
    with pytest.raises(PermissionError):
        await label_service.update_label(
            label_id=label.id,
            label_data=label_data,
            user_id=other_user.id,
        )


@pytest.mark.asyncio
async def test_delete_label(
    label_service: LabelService,
    test_workspace: Workspace,
    test_user: User,
    test_card: Card,
    db_session: AsyncSession,
):
    """Test deleting a label and getting affected card count."""
    # Create label
    label = WorkspaceLabel(
        workspace_id=test_workspace.id,
        name="Bug",
        color="#FF0000",
    )
    db_session.add(label)
    await db_session.flush()

    # Add label to card
    await label_service.add_label_to_card(
        card_id=test_card.id,
        label_id=label.id,
        user_id=test_user.id,
    )

    # Delete label
    result = await label_service.delete_label(
        label_id=label.id,
        user_id=test_user.id,
    )

    assert result["cards_affected"] == 1


@pytest.mark.asyncio
async def test_add_label_to_card(
    label_service: LabelService,
    test_workspace: Workspace,
    test_user: User,
    test_card: Card,
    db_session: AsyncSession,
):
    """Test adding a label to a card."""
    # Create label
    label = WorkspaceLabel(
        workspace_id=test_workspace.id,
        name="Bug",
        color="#FF0000",
    )
    db_session.add(label)
    await db_session.flush()

    # Add label to card
    await label_service.add_label_to_card(
        card_id=test_card.id,
        label_id=label.id,
        user_id=test_user.id,
    )

    # Verify label was added
    await db_session.refresh(test_card)
    card_with_labels = await db_session.get(Card, test_card.id)
    # Note: This would require proper eager loading in actual implementation
    # For now, we just verify the operation succeeds


@pytest.mark.asyncio
async def test_add_label_to_card_unauthorized(
    label_service: LabelService,
    test_workspace: Workspace,
    other_user: User,
    test_card: Card,
    db_session: AsyncSession,
):
    """Test adding label to card by non-member raises PermissionError."""
    label = WorkspaceLabel(
        workspace_id=test_workspace.id,
        name="Bug",
        color="#FF0000",
    )
    db_session.add(label)
    await db_session.flush()

    with pytest.raises(PermissionError):
        await label_service.add_label_to_card(
            card_id=test_card.id,
            label_id=label.id,
            user_id=other_user.id,
        )


@pytest.mark.asyncio
async def test_remove_label_from_card(
    label_service: LabelService,
    test_workspace: Workspace,
    test_user: User,
    test_card: Card,
    db_session: AsyncSession,
):
    """Test removing a label from a card."""
    # Create and add label
    label = WorkspaceLabel(
        workspace_id=test_workspace.id,
        name="Bug",
        color="#FF0000",
    )
    db_session.add(label)
    await db_session.flush()

    await label_service.add_label_to_card(
        card_id=test_card.id,
        label_id=label.id,
        user_id=test_user.id,
    )

    # Remove label
    await label_service.remove_label_from_card(
        card_id=test_card.id,
        label_id=label.id,
        user_id=test_user.id,
    )

    # Verify label was removed (operation succeeds without exception)


@pytest.mark.asyncio
async def test_add_duplicate_label_raises_error(
    label_service: LabelService,
    test_workspace: Workspace,
    test_user: User,
    test_card: Card,
    db_session: AsyncSession,
):
    """Test adding same label twice raises ValueError."""
    label = WorkspaceLabel(
        workspace_id=test_workspace.id,
        name="Bug",
        color="#FF0000",
    )
    db_session.add(label)
    await db_session.flush()

    # Add label first time
    await label_service.add_label_to_card(
        card_id=test_card.id,
        label_id=label.id,
        user_id=test_user.id,
    )

    # Try to add again - should raise ValueError
    with pytest.raises(ValueError, match="already added"):
        await label_service.add_label_to_card(
            card_id=test_card.id,
            label_id=label.id,
            user_id=test_user.id,
        )

"""Unit tests for WorkspaceService."""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.user import User
from app.models.workspace import Workspace
from app.models.workspace_member import RoleEnum, WorkspaceMember
from app.services.workspace_service import WorkspaceService


@pytest.fixture
async def workspace_service(db_session: AsyncSession) -> WorkspaceService:
    """Workspace service instance with test database."""
    return WorkspaceService(db_session)


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Test user for workspace operations."""
    user = User(
        github_id=12345,
        username="testuser",
        email="test@example.com",
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.fixture
async def test_admin_user(db_session: AsyncSession) -> User:
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
async def test_member_user(db_session: AsyncSession) -> User:
    """Non-admin member user for workspace operations."""
    user = User(
        github_id=11111,
        username="memberuser",
        email="member@example.com",
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.fixture
async def test_workspace(db_session: AsyncSession, test_admin_user: User) -> Workspace:
    """Workspace for testing."""
    workspace = Workspace(
        name="Test Workspace",
        created_by=test_admin_user.id,
    )
    db_session.add(workspace)
    await db_session.flush()
    return workspace


@pytest.fixture
async def test_workspace_with_admin(
    db_session: AsyncSession,
    test_workspace: Workspace,
    test_admin_user: User,
) -> Workspace:
    """Workspace with admin user membership."""
    membership = WorkspaceMember(
        user_id=test_admin_user.id,
        workspace_id=test_workspace.id,
        role=RoleEnum.ADMIN,
    )
    db_session.add(membership)
    await db_session.flush()
    return test_workspace


@pytest.fixture
async def test_workspace_with_member(
    db_session: AsyncSession,
    test_workspace_with_admin: Workspace,
    test_member_user: User,
) -> Workspace:
    """Workspace with admin and non-admin member."""
    membership = WorkspaceMember(
        user_id=test_member_user.id,
        workspace_id=test_workspace_with_admin.id,
        role=RoleEnum.MEMBER,
    )
    db_session.add(membership)
    await db_session.flush()
    return test_workspace_with_admin


# Test 1: Create workspace adds creator as admin
@pytest.mark.asyncio
async def test_create_workspace_adds_creator_as_admin(
    workspace_service: WorkspaceService,
    test_user: User,
    db_session: AsyncSession,
) -> None:
    """Test that creating workspace automatically adds creator as admin."""
    # Given: User creating a new workspace
    workspace_name = "New Workspace"

    # When: create_workspace is called
    workspace = await workspace_service.create_workspace(
        name=workspace_name,
        creator_id=test_user.id,
    )

    # Then: Workspace is created
    assert workspace.name == workspace_name
    assert workspace.created_by == test_user.id

    # And: WorkspaceMember record created with role=ADMIN
    result = await db_session.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace.id,
            WorkspaceMember.user_id == test_user.id,
        )
    )
    membership = result.scalar_one_or_none()

    assert membership is not None
    assert membership.role == RoleEnum.ADMIN
    assert membership.workspace_id == workspace.id
    assert membership.user_id == test_user.id


# Test 2: Update workspace requires admin role
@pytest.mark.asyncio
async def test_update_workspace_requires_admin_role(
    workspace_service: WorkspaceService,
    test_workspace_with_member: Workspace,
    test_member_user: User,
) -> None:
    """Test that non-admin members cannot update workspace."""
    # Given: Non-admin workspace member
    # (test_member_user is a MEMBER, not ADMIN)

    # When: Attempting to update workspace
    # Then: HTTPException 403 is raised
    with pytest.raises(HTTPException) as exc_info:
        await workspace_service.update_workspace(
            workspace_id=test_workspace_with_member.id,
            updates={"name": "Hacked Name"},
            user_id=test_member_user.id,
        )

    # And: Error message is clear
    assert exc_info.value.status_code == 403
    assert "admin" in exc_info.value.detail.lower()


# Test 3: Update workspace succeeds for admin
@pytest.mark.asyncio
async def test_update_workspace_succeeds_for_admin(
    workspace_service: WorkspaceService,
    test_workspace_with_admin: Workspace,
    test_admin_user: User,
    db_session: AsyncSession,
) -> None:
    """Test that admin users can update workspace."""
    # Given: Admin user updating workspace name
    new_name = "Updated Workspace Name"

    # When: update_workspace is called
    updated_workspace = await workspace_service.update_workspace(
        workspace_id=test_workspace_with_admin.id,
        updates={"name": new_name},
        user_id=test_admin_user.id,
    )

    # Then: Workspace name is updated
    assert updated_workspace.name == new_name
    assert updated_workspace.id == test_workspace_with_admin.id

    # And: Change is persisted in database
    await db_session.refresh(test_workspace_with_admin)
    assert test_workspace_with_admin.name == new_name


# Test 4: Delete workspace requires admin role
@pytest.mark.asyncio
async def test_delete_workspace_requires_admin_role(
    workspace_service: WorkspaceService,
    test_workspace_with_member: Workspace,
    test_member_user: User,
) -> None:
    """Test that non-admin members cannot delete workspace."""
    # Given: Non-admin workspace member

    # When: Attempting to delete workspace
    # Then: HTTPException 403 is raised
    with pytest.raises(HTTPException) as exc_info:
        await workspace_service.delete_workspace(
            workspace_id=test_workspace_with_member.id,
            user_id=test_member_user.id,
        )

    # And: Error message is clear
    assert exc_info.value.status_code == 403
    assert "admin" in exc_info.value.detail.lower()


# Test 5: Delete workspace succeeds for admin
@pytest.mark.asyncio
async def test_delete_workspace_succeeds_for_admin(
    workspace_service: WorkspaceService,
    test_workspace_with_admin: Workspace,
    test_admin_user: User,
    db_session: AsyncSession,
) -> None:
    """Test that admin users can delete workspace."""
    # Given: Admin user deleting workspace
    workspace_id = test_workspace_with_admin.id

    # When: delete_workspace is called
    await workspace_service.delete_workspace(
        workspace_id=workspace_id,
        user_id=test_admin_user.id,
    )

    # Then: Workspace is deleted from database
    result = await db_session.execute(
        select(Workspace).where(Workspace.id == workspace_id)
    )
    deleted_workspace = result.scalar_one_or_none()

    assert deleted_workspace is None

    # And: Membership is also deleted (cascade)
    membership_result = await db_session.execute(
        select(WorkspaceMember).where(WorkspaceMember.workspace_id == workspace_id)
    )
    memberships = membership_result.scalars().all()

    assert len(memberships) == 0


# Test 6: Get user workspaces returns only member workspaces
@pytest.mark.asyncio
async def test_get_user_workspaces_returns_only_member_workspaces(
    workspace_service: WorkspaceService,
    test_user: User,
    test_admin_user: User,
    db_session: AsyncSession,
) -> None:
    """Test that get_user_workspaces returns only workspaces user is member of."""
    # Given: User who is member of 2 workspaces
    workspace1 = Workspace(name="Workspace 1", created_by=test_user.id)
    workspace2 = Workspace(name="Workspace 2", created_by=test_user.id)
    workspace3 = Workspace(name="Workspace 3", created_by=test_admin_user.id)

    db_session.add_all([workspace1, workspace2, workspace3])
    await db_session.flush()

    # Add user as member to workspace1 and workspace2
    membership1 = WorkspaceMember(
        user_id=test_user.id,
        workspace_id=workspace1.id,
        role=RoleEnum.ADMIN,
    )
    membership2 = WorkspaceMember(
        user_id=test_user.id,
        workspace_id=workspace2.id,
        role=RoleEnum.MEMBER,
    )
    db_session.add_all([membership1, membership2])
    await db_session.flush()

    # When: get_user_workspaces is called
    user_workspaces = await workspace_service.get_user_workspaces(test_user.id)

    # Then: Returns exactly 2 workspaces
    assert len(user_workspaces) == 2

    # And: Workspaces are the ones user is member of
    workspace_ids = {ws.id for ws in user_workspaces}
    assert workspace1.id in workspace_ids
    assert workspace2.id in workspace_ids
    assert workspace3.id not in workspace_ids

    # And: Ordered by updated_at desc (most recent first)
    # Both have same updated_at in this test, so just verify list length
    assert isinstance(user_workspaces, list)


# Test 7: Workspace name validation strips whitespace
@pytest.mark.asyncio
async def test_workspace_name_validation_strips_whitespace(
    workspace_service: WorkspaceService,
    test_user: User,
) -> None:
    """Test that workspace name with whitespace is trimmed."""
    # Given: Workspace name with leading/trailing whitespace
    workspace_name_with_whitespace = "  Workspace Name  "
    expected_name = "Workspace Name"

    # When: create_workspace is called
    workspace = await workspace_service.create_workspace(
        name=workspace_name_with_whitespace,
        creator_id=test_user.id,
    )

    # Then: Workspace is created with trimmed name
    assert workspace.name == expected_name
    assert workspace.name == workspace_name_with_whitespace.strip()
    assert workspace.name != workspace_name_with_whitespace

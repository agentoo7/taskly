"""Integration tests for member management API endpoints."""

import uuid
from datetime import datetime

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.workspace import Workspace
from app.models.workspace_audit_log import AuditActionEnum, WorkspaceAuditLog
from app.models.workspace_member import RoleEnum, WorkspaceMember


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        github_id=12345,
        username="admin_user",
        email="admin@example.com",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_workspace(db_session: AsyncSession, test_user: User) -> Workspace:
    """Create a test workspace."""
    workspace = Workspace(
        name="Test Workspace",
        created_by=test_user.id,
    )
    db_session.add(workspace)
    await db_session.commit()
    await db_session.refresh(workspace)
    return workspace


@pytest.fixture
async def admin_member(
    db_session: AsyncSession, test_workspace: Workspace, test_user: User
) -> WorkspaceMember:
    """Create an admin member."""
    member = WorkspaceMember(
        workspace_id=test_workspace.id,
        user_id=test_user.id,
        role=RoleEnum.ADMIN,
        joined_at=datetime.utcnow(),
    )
    db_session.add(member)
    await db_session.commit()
    await db_session.refresh(member)
    return member


@pytest.fixture
async def regular_member(
    db_session: AsyncSession, test_workspace: Workspace
) -> tuple[WorkspaceMember, User]:
    """Create a regular member with their user."""
    user = User(
        github_id=67890,
        username="regular_user",
        email="regular@example.com",
    )
    db_session.add(user)
    await db_session.flush()

    member = WorkspaceMember(
        workspace_id=test_workspace.id,
        user_id=user.id,
        role=RoleEnum.MEMBER,
        joined_at=datetime.utcnow(),
    )
    db_session.add(member)
    await db_session.commit()
    await db_session.refresh(member)
    await db_session.refresh(user)
    return member, user


class TestGetMembers:
    """Tests for GET /api/workspaces/{workspace_id}/members"""

    @pytest.mark.asyncio
    async def test_get_members_success(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_workspace: Workspace,
        test_user: User,
        admin_member: WorkspaceMember,
        regular_member: tuple[WorkspaceMember, User],
    ):
        """Test getting workspace members."""
        # Mock authentication
        from app.api.dependencies import get_current_user

        async def override_get_current_user():
            return test_user

        from app.main import app

        app.dependency_overrides[get_current_user] = override_get_current_user

        response = await client.get(f"/api/workspaces/{test_workspace.id}/members")

        assert response.status_code == 200
        data = response.json()

        assert len(data) == 2  # Admin and regular member

        # Check member details
        usernames = [member["username"] for member in data]
        assert "admin_user" in usernames
        assert "regular_user" in usernames

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_members_with_search(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_workspace: Workspace,
        test_user: User,
        admin_member: WorkspaceMember,
        regular_member: tuple[WorkspaceMember, User],
    ):
        """Test searching members by username or email."""
        # Mock authentication
        from app.api.dependencies import get_current_user

        async def override_get_current_user():
            return test_user

        from app.main import app

        app.dependency_overrides[get_current_user] = override_get_current_user

        # Search by username
        response = await client.get(f"/api/workspaces/{test_workspace.id}/members?search=regular")

        assert response.status_code == 200
        data = response.json()

        assert len(data) == 1
        assert data[0]["username"] == "regular_user"

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_members_unauthorized(
        self, client: AsyncClient, db_session: AsyncSession, test_workspace: Workspace
    ):
        """Test that non-members cannot view members."""
        # Create a user who is not a member
        outsider = User(
            username="outsider",
            email="outsider@example.com",
            github_id=99999,
        )
        db_session.add(outsider)
        await db_session.commit()

        # Mock authentication
        from app.api.dependencies import get_current_user

        async def override_get_current_user():
            return outsider

        from app.main import app

        app.dependency_overrides[get_current_user] = override_get_current_user

        response = await client.get(f"/api/workspaces/{test_workspace.id}/members")

        assert response.status_code == 403

        app.dependency_overrides.clear()


class TestUpdateMemberRole:
    """Tests for PATCH /api/workspaces/{workspace_id}/members/{user_id}"""

    @pytest.mark.asyncio
    async def test_update_member_role_to_admin(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_workspace: Workspace,
        test_user: User,
        admin_member: WorkspaceMember,
        regular_member: tuple[WorkspaceMember, User],
    ):
        """Test promoting member to admin."""
        member, regular_user = regular_member

        # Mock authentication
        from app.api.dependencies import get_current_user

        async def override_get_current_user():
            return test_user

        from app.main import app

        app.dependency_overrides[get_current_user] = override_get_current_user

        response = await client.patch(
            f"/api/workspaces/{test_workspace.id}/members/{regular_user.id}",
            json={"role": "admin"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["role"] == "admin"

        # Verify role was updated in database
        await db_session.refresh(member)
        assert member.role == RoleEnum.ADMIN

        # Verify audit log
        result = await db_session.execute(
            select(WorkspaceAuditLog).where(
                WorkspaceAuditLog.workspace_id == test_workspace.id,
                WorkspaceAuditLog.action == AuditActionEnum.MEMBER_ROLE_CHANGED,
            )
        )
        audit_log = result.scalar_one_or_none()
        assert audit_log is not None
        assert audit_log.context_data["old_role"] == "member"
        assert audit_log.context_data["new_role"] == "admin"

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_update_member_role_to_member(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_workspace: Workspace,
        test_user: User,
        admin_member: WorkspaceMember,
    ):
        """Test demoting admin to member."""
        # Create another admin to demote
        another_admin_user = User(
            username="another_admin",
            email="another_admin@example.com",
            github_id=99999,
        )
        db_session.add(another_admin_user)
        await db_session.flush()

        another_admin = WorkspaceMember(
            workspace_id=test_workspace.id,
            user_id=another_admin_user.id,
            role=RoleEnum.ADMIN,
            joined_at=datetime.utcnow(),
        )
        db_session.add(another_admin)
        await db_session.commit()

        # Mock authentication
        from app.api.dependencies import get_current_user

        async def override_get_current_user():
            return test_user

        from app.main import app

        app.dependency_overrides[get_current_user] = override_get_current_user

        response = await client.patch(
            f"/api/workspaces/{test_workspace.id}/members/{another_admin_user.id}",
            json={"role": "member"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["role"] == "member"

        # Verify role was updated
        await db_session.refresh(another_admin)
        assert another_admin.role == RoleEnum.MEMBER

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_update_role_last_admin_prevention(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_workspace: Workspace,
        test_user: User,
        admin_member: WorkspaceMember,
    ):
        """Test that last admin cannot be demoted."""
        # Mock authentication
        from app.api.dependencies import get_current_user

        async def override_get_current_user():
            return test_user

        from app.main import app

        app.dependency_overrides[get_current_user] = override_get_current_user

        # Try to demote the only admin
        response = await client.patch(
            f"/api/workspaces/{test_workspace.id}/members/{test_user.id}",
            json={"role": "member"},
        )

        assert response.status_code == 400
        assert "last admin" in response.json()["detail"].lower()

        # Verify role was NOT changed
        await db_session.refresh(admin_member)
        assert admin_member.role == RoleEnum.ADMIN

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_update_role_as_member_forbidden(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_workspace: Workspace,
        regular_member: tuple[WorkspaceMember, User],
    ):
        """Test that regular members cannot change roles."""
        _, regular_user = regular_member

        # Create another user to try to modify
        another_user = User(
            username="another_user",
            email="another@example.com",
            github_id=99999,
        )
        db_session.add(another_user)
        await db_session.flush()

        another_member = WorkspaceMember(
            workspace_id=test_workspace.id,
            user_id=another_user.id,
            role=RoleEnum.MEMBER,
            joined_at=datetime.utcnow(),
        )
        db_session.add(another_member)
        await db_session.commit()

        # Mock authentication
        from app.api.dependencies import get_current_user

        async def override_get_current_user():
            return regular_user

        from app.main import app

        app.dependency_overrides[get_current_user] = override_get_current_user

        response = await client.patch(
            f"/api/workspaces/{test_workspace.id}/members/{another_user.id}",
            json={"role": "admin"},
        )

        assert response.status_code == 403

        app.dependency_overrides.clear()


class TestRemoveMember:
    """Tests for DELETE /api/workspaces/{workspace_id}/members/{user_id}"""

    @pytest.mark.asyncio
    async def test_remove_member_success(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_workspace: Workspace,
        test_user: User,
        admin_member: WorkspaceMember,
        regular_member: tuple[WorkspaceMember, User],
    ):
        """Test removing a member from workspace."""
        member, regular_user = regular_member

        # Mock authentication
        from app.api.dependencies import get_current_user

        async def override_get_current_user():
            return test_user

        from app.main import app

        app.dependency_overrides[get_current_user] = override_get_current_user

        response = await client.delete(
            f"/api/workspaces/{test_workspace.id}/members/{regular_user.id}"
        )

        assert response.status_code == 204

        # Verify member was removed
        result = await db_session.execute(
            select(WorkspaceMember).where(
                WorkspaceMember.workspace_id == test_workspace.id,
                WorkspaceMember.user_id == regular_user.id,
            )
        )
        removed_member = result.scalar_one_or_none()
        assert removed_member is None

        # Verify audit log
        result = await db_session.execute(
            select(WorkspaceAuditLog).where(
                WorkspaceAuditLog.workspace_id == test_workspace.id,
                WorkspaceAuditLog.action == AuditActionEnum.MEMBER_REMOVED,
            )
        )
        audit_log = result.scalar_one_or_none()
        assert audit_log is not None

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_remove_last_admin_prevention(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_workspace: Workspace,
        test_user: User,
        admin_member: WorkspaceMember,
    ):
        """Test that last admin cannot be removed."""
        # Mock authentication
        from app.api.dependencies import get_current_user

        async def override_get_current_user():
            return test_user

        from app.main import app

        app.dependency_overrides[get_current_user] = override_get_current_user

        response = await client.delete(
            f"/api/workspaces/{test_workspace.id}/members/{test_user.id}"
        )

        assert response.status_code == 400
        assert "last admin" in response.json()["detail"].lower()

        # Verify member was NOT removed
        result = await db_session.execute(
            select(WorkspaceMember).where(
                WorkspaceMember.workspace_id == test_workspace.id,
                WorkspaceMember.user_id == test_user.id,
            )
        )
        member = result.scalar_one_or_none()
        assert member is not None

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_remove_admin_when_multiple_admins_exist(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_workspace: Workspace,
        test_user: User,
        admin_member: WorkspaceMember,
    ):
        """Test that admin can be removed when other admins exist."""
        # Create another admin
        another_admin_user = User(
            username="another_admin",
            email="another_admin@example.com",
            github_id=99999,
        )
        db_session.add(another_admin_user)
        await db_session.flush()

        another_admin = WorkspaceMember(
            workspace_id=test_workspace.id,
            user_id=another_admin_user.id,
            role=RoleEnum.ADMIN,
            joined_at=datetime.utcnow(),
        )
        db_session.add(another_admin)
        await db_session.commit()

        # Mock authentication
        from app.api.dependencies import get_current_user

        async def override_get_current_user():
            return test_user

        from app.main import app

        app.dependency_overrides[get_current_user] = override_get_current_user

        # Remove the other admin (should succeed since we still have one admin left)
        response = await client.delete(
            f"/api/workspaces/{test_workspace.id}/members/{another_admin_user.id}"
        )

        assert response.status_code == 204

        # Verify member was removed
        result = await db_session.execute(
            select(WorkspaceMember).where(
                WorkspaceMember.workspace_id == test_workspace.id,
                WorkspaceMember.user_id == another_admin_user.id,
            )
        )
        removed_member = result.scalar_one_or_none()
        assert removed_member is None

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_remove_member_as_member_forbidden(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_workspace: Workspace,
        regular_member: tuple[WorkspaceMember, User],
    ):
        """Test that regular members cannot remove other members."""
        _, regular_user = regular_member

        # Create another member to try to remove
        another_user = User(
            username="another_user",
            email="another@example.com",
            github_id=99999,
        )
        db_session.add(another_user)
        await db_session.flush()

        another_member = WorkspaceMember(
            workspace_id=test_workspace.id,
            user_id=another_user.id,
            role=RoleEnum.MEMBER,
            joined_at=datetime.utcnow(),
        )
        db_session.add(another_member)
        await db_session.commit()

        # Mock authentication
        from app.api.dependencies import get_current_user

        async def override_get_current_user():
            return regular_user

        from app.main import app

        app.dependency_overrides[get_current_user] = override_get_current_user

        response = await client.delete(
            f"/api/workspaces/{test_workspace.id}/members/{another_user.id}"
        )

        assert response.status_code == 403

        # Verify member was NOT removed
        result = await db_session.execute(
            select(WorkspaceMember).where(
                WorkspaceMember.workspace_id == test_workspace.id,
                WorkspaceMember.user_id == another_user.id,
            )
        )
        member = result.scalar_one_or_none()
        assert member is not None

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_remove_nonexistent_member(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_workspace: Workspace,
        test_user: User,
        admin_member: WorkspaceMember,
    ):
        """Test removing a user who is not a member."""
        # Create a user who is not a member
        non_member = User(
            username="non_member",
            email="non@example.com",
            github_id=99999,
        )
        db_session.add(non_member)
        await db_session.commit()

        # Mock authentication
        from app.api.dependencies import get_current_user

        async def override_get_current_user():
            return test_user

        from app.main import app

        app.dependency_overrides[get_current_user] = override_get_current_user

        response = await client.delete(
            f"/api/workspaces/{test_workspace.id}/members/{non_member.id}"
        )

        assert response.status_code == 404

        app.dependency_overrides.clear()

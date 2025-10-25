"""End-to-end tests for complete invitation workflow."""

import uuid
from datetime import datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.workspace import Workspace
from app.models.workspace_audit_log import AuditActionEnum, WorkspaceAuditLog
from app.models.workspace_invitation import WorkspaceInvitation
from app.models.workspace_member import RoleEnum, WorkspaceMember


@pytest.fixture
async def admin_user(db_session: AsyncSession) -> User:
    """Create an admin user."""
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
async def workspace(db_session: AsyncSession, admin_user: User) -> Workspace:
    """Create a test workspace."""
    workspace = Workspace(
        name="Test Workspace",
        created_by=admin_user.id,
    )
    db_session.add(workspace)
    await db_session.commit()
    await db_session.refresh(workspace)
    return workspace


@pytest.fixture
async def admin_member(
    db_session: AsyncSession, workspace: Workspace, admin_user: User
) -> WorkspaceMember:
    """Make admin_user an admin member of workspace."""
    member = WorkspaceMember(
        workspace_id=workspace.id,
        user_id=admin_user.id,
        role=RoleEnum.ADMIN,
        joined_at=datetime.utcnow(),
    )
    db_session.add(member)
    await db_session.commit()
    await db_session.refresh(member)
    return member


@pytest.fixture
async def invitee_user(db_session: AsyncSession) -> User:
    """Create a user who will be invited."""
    user = User(
        github_id=67890,
        username="invitee_user",
        email="invitee@example.com",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


class TestInvitationE2EFlow:
    """End-to-end tests for complete invitation flow."""

    @pytest.mark.asyncio
    async def test_full_invitation_flow_from_send_to_acceptance(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        workspace: Workspace,
        admin_user: User,
        admin_member: WorkspaceMember,
        invitee_user: User,
    ):
        """
        Test the complete invitation workflow:
        1. Admin creates invitation
        2. Invitation is saved in database with correct details
        3. Invitation can be retrieved by token
        4. Invitee accepts invitation
        5. Invitee becomes member of workspace
        6. Invitation is marked as accepted
        7. Audit logs are created for all actions
        8. Invitee can access workspace
        """
        from app.api.dependencies import get_current_user
        from app.main import app

        # ========== STEP 1: Admin creates invitation ==========
        async def override_get_current_user_admin():
            return admin_user

        app.dependency_overrides[get_current_user] = override_get_current_user_admin

        create_response = await client.post(
            f"/api/workspaces/{workspace.id}/invitations",
            json={"emails": ["invitee@example.com"], "role": "member"},
        )

        assert create_response.status_code == 201, f"Failed to create invitation: {create_response.text}"
        invitations_data = create_response.json()
        assert len(invitations_data) == 1
        assert invitations_data[0]["email"] == "invitee@example.com"
        assert invitations_data[0]["role"] == "member"

        # ========== STEP 2: Verify invitation in database ==========
        result = await db_session.execute(
            select(WorkspaceInvitation).where(
                WorkspaceInvitation.workspace_id == workspace.id,
                WorkspaceInvitation.email == "invitee@example.com",
            )
        )
        invitation = result.scalar_one()
        assert invitation is not None
        assert invitation.role == RoleEnum.MEMBER
        assert invitation.invited_by == admin_user.id
        assert invitation.accepted_at is None
        assert invitation.expires_at > datetime.utcnow()
        invitation_token = invitation.token

        # Verify INVITATION_CREATED audit log
        result = await db_session.execute(
            select(WorkspaceAuditLog).where(
                WorkspaceAuditLog.workspace_id == workspace.id,
                WorkspaceAuditLog.action == AuditActionEnum.INVITATION_CREATED,
                WorkspaceAuditLog.actor_id == admin_user.id,
            )
        )
        create_audit_log = result.scalar_one_or_none()
        assert create_audit_log is not None

        app.dependency_overrides.clear()

        # ========== STEP 3: Retrieve invitation details (public endpoint) ==========
        details_response = await client.get(f"/api/invitations/{invitation_token}")

        assert details_response.status_code == 200
        details_data = details_response.json()
        assert details_data["email"] == "invitee@example.com"
        assert details_data["workspace_name"] == "Test Workspace"
        assert details_data["role"] == "member"
        assert details_data["is_expired"] is False
        assert details_data["is_accepted"] is False

        # ========== STEP 4: Invitee accepts invitation ==========
        async def override_get_current_user_invitee():
            return invitee_user

        app.dependency_overrides[get_current_user] = override_get_current_user_invitee

        accept_response = await client.post(f"/api/invitations/{invitation_token}/accept")

        assert accept_response.status_code == 200, f"Failed to accept invitation: {accept_response.text}"
        accept_data = accept_response.json()
        assert accept_data["workspace_id"] == str(workspace.id)
        assert "message" in accept_data

        # ========== STEP 5: Verify invitee is now a member ==========
        result = await db_session.execute(
            select(WorkspaceMember).where(
                WorkspaceMember.workspace_id == workspace.id,
                WorkspaceMember.user_id == invitee_user.id,
            )
        )
        new_member = result.scalar_one()
        assert new_member is not None
        assert new_member.role == RoleEnum.MEMBER
        assert new_member.joined_at is not None

        # ========== STEP 6: Verify invitation is marked as accepted ==========
        await db_session.refresh(invitation)
        assert invitation.accepted_at is not None
        assert invitation.accepted_by == invitee_user.id

        # Verify INVITATION_ACCEPTED audit log
        result = await db_session.execute(
            select(WorkspaceAuditLog).where(
                WorkspaceAuditLog.workspace_id == workspace.id,
                WorkspaceAuditLog.action == AuditActionEnum.INVITATION_ACCEPTED,
                WorkspaceAuditLog.actor_id == invitee_user.id,
            )
        )
        accept_audit_log = result.scalar_one_or_none()
        assert accept_audit_log is not None

        # ========== STEP 7: Verify invitee can access workspace ==========
        workspace_response = await client.get(f"/api/workspaces/{workspace.id}")

        assert workspace_response.status_code == 200
        workspace_data = workspace_response.json()
        assert workspace_data["id"] == str(workspace.id)
        assert workspace_data["name"] == "Test Workspace"

        # ========== STEP 8: Verify invitee can see workspace members ==========
        members_response = await client.get(f"/api/workspaces/{workspace.id}/members")

        assert members_response.status_code == 200
        members_data = members_response.json()
        assert len(members_data) == 2  # Admin + Invitee

        member_emails = [m["email"] for m in members_data]
        assert "admin@example.com" in member_emails
        assert "invitee@example.com" in member_emails

        # ========== STEP 9: Verify cannot accept same invitation twice ==========
        duplicate_accept_response = await client.post(
            f"/api/invitations/{invitation_token}/accept"
        )

        assert duplicate_accept_response.status_code == 400
        assert "already" in duplicate_accept_response.json()["detail"].lower()

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_invitation_flow_with_admin_role(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        workspace: Workspace,
        admin_user: User,
        admin_member: WorkspaceMember,
        invitee_user: User,
    ):
        """Test invitation flow where invitee is assigned admin role."""
        from app.api.dependencies import get_current_user
        from app.main import app

        # Admin creates invitation with admin role
        async def override_get_current_user_admin():
            return admin_user

        app.dependency_overrides[get_current_user] = override_get_current_user_admin

        create_response = await client.post(
            f"/api/workspaces/{workspace.id}/invitations",
            json={"emails": ["invitee@example.com"], "role": "admin"},
        )

        assert create_response.status_code == 201
        invitations_data = create_response.json()
        assert invitations_data[0]["role"] == "admin"

        # Get invitation token
        result = await db_session.execute(
            select(WorkspaceInvitation).where(
                WorkspaceInvitation.workspace_id == workspace.id,
                WorkspaceInvitation.email == "invitee@example.com",
            )
        )
        invitation = result.scalar_one()
        invitation_token = invitation.token

        app.dependency_overrides.clear()

        # Invitee accepts invitation
        async def override_get_current_user_invitee():
            return invitee_user

        app.dependency_overrides[get_current_user] = override_get_current_user_invitee

        accept_response = await client.post(f"/api/invitations/{invitation_token}/accept")
        assert accept_response.status_code == 200

        # Verify invitee has admin role
        result = await db_session.execute(
            select(WorkspaceMember).where(
                WorkspaceMember.workspace_id == workspace.id,
                WorkspaceMember.user_id == invitee_user.id,
            )
        )
        new_member = result.scalar_one()
        assert new_member.role == RoleEnum.ADMIN

        # Verify invitee can invite other members (admin privilege)
        invite_another_response = await client.post(
            f"/api/workspaces/{workspace.id}/invitations",
            json={"emails": ["another@example.com"], "role": "member"},
        )
        assert invite_another_response.status_code == 201

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_invitation_flow_with_expiration(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        workspace: Workspace,
        admin_user: User,
        admin_member: WorkspaceMember,
        invitee_user: User,
    ):
        """Test that expired invitations cannot be accepted."""
        # Create invitation that's already expired
        expired_invitation = WorkspaceInvitation(
            workspace_id=workspace.id,
            email="invitee@example.com",
            token="expired_token_123",
            role=RoleEnum.MEMBER,
            invited_by=admin_user.id,
            expires_at=datetime.utcnow() - timedelta(days=1),  # Expired yesterday
            created_at=datetime.utcnow() - timedelta(days=8),
            updated_at=datetime.utcnow() - timedelta(days=8),
        )
        db_session.add(expired_invitation)
        await db_session.commit()

        from app.api.dependencies import get_current_user
        from app.main import app

        async def override_get_current_user_invitee():
            return invitee_user

        app.dependency_overrides[get_current_user] = override_get_current_user_invitee

        # Try to accept expired invitation
        accept_response = await client.post("/api/invitations/expired_token_123/accept")

        assert accept_response.status_code == 400
        assert "expired" in accept_response.json()["detail"].lower()

        # Verify no membership was created
        result = await db_session.execute(
            select(WorkspaceMember).where(
                WorkspaceMember.workspace_id == workspace.id,
                WorkspaceMember.user_id == invitee_user.id,
            )
        )
        member = result.scalar_one_or_none()
        assert member is None

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_resend_invitation_refreshes_token_and_expiration(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        workspace: Workspace,
        admin_user: User,
        admin_member: WorkspaceMember,
    ):
        """Test that resending invitation generates new token and extends expiration."""
        from app.api.dependencies import get_current_user
        from app.main import app

        # Create invitation
        async def override_get_current_user_admin():
            return admin_user

        app.dependency_overrides[get_current_user] = override_get_current_user_admin

        create_response = await client.post(
            f"/api/workspaces/{workspace.id}/invitations",
            json={"emails": ["newinvite@example.com"], "role": "member"},
        )
        assert create_response.status_code == 201

        # Get original invitation
        result = await db_session.execute(
            select(WorkspaceInvitation).where(
                WorkspaceInvitation.workspace_id == workspace.id,
                WorkspaceInvitation.email == "newinvite@example.com",
            )
        )
        invitation = result.scalar_one()
        original_token = invitation.token
        original_expires_at = invitation.expires_at

        # Resend invitation
        resend_response = await client.post(
            f"/api/workspaces/{workspace.id}/invitations/{invitation.id}/resend"
        )
        assert resend_response.status_code == 200

        # Verify token and expiration were refreshed
        await db_session.refresh(invitation)
        assert invitation.token != original_token, "Token should be refreshed"
        assert invitation.expires_at > original_expires_at, "Expiration should be extended"

        # Verify old token no longer works
        old_token_response = await client.get(f"/api/invitations/{original_token}")
        assert old_token_response.status_code == 404

        # Verify new token works
        new_token_response = await client.get(f"/api/invitations/{invitation.token}")
        assert new_token_response.status_code == 200

        app.dependency_overrides.clear()

"""Integration tests for invitation API endpoints."""

import uuid
from datetime import datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.workspace import Workspace
from app.models.workspace_audit_log import WorkspaceAuditLog
from app.models.workspace_invitation import WorkspaceInvitation
from app.models.workspace_member import RoleEnum, WorkspaceMember
from app.services.invitation_service import InvitationService


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        github_id=12345,
        username="testuser",
        email="test@example.com",
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
        username="regularuser",
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


class TestCreateInvitations:
    """Tests for POST /api/workspaces/{workspace_id}/invitations"""

    @pytest.mark.asyncio
    async def test_create_invitations_as_admin(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_workspace: Workspace,
        test_user: User,
        admin_member: WorkspaceMember,
    ):
        """Test that admin can create invitations."""
        # Mock authentication
        from app.api.dependencies import get_current_user

        async def override_get_current_user():
            return test_user

        from app.main import app

        app.dependency_overrides[get_current_user] = override_get_current_user

        payload = {"emails": ["newuser1@example.com", "newuser2@example.com"], "role": "member"}

        response = await client.post(
            f"/api/workspaces/{test_workspace.id}/invitations", json=payload
        )

        assert response.status_code == 201
        data = response.json()

        assert len(data) == 2
        assert data[0]["email"] == "newuser1@example.com"
        assert data[1]["email"] == "newuser2@example.com"
        assert data[0]["role"] == "member"

        # Verify invitations in database
        result = await db_session.execute(
            select(WorkspaceInvitation).where(WorkspaceInvitation.workspace_id == test_workspace.id)
        )
        invitations = result.scalars().all()
        assert len(invitations) == 2

        # Verify audit logs
        result = await db_session.execute(
            select(WorkspaceAuditLog).where(WorkspaceAuditLog.workspace_id == test_workspace.id)
        )
        audit_logs = result.scalars().all()
        assert len(audit_logs) == 2  # One per invitation

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_create_invitations_as_member_forbidden(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_workspace: Workspace,
        regular_member: tuple[WorkspaceMember, User],
    ):
        """Test that regular members cannot create invitations."""
        _, regular_user = regular_member

        # Mock authentication
        from app.api.dependencies import get_current_user

        async def override_get_current_user():
            return regular_user

        from app.main import app

        app.dependency_overrides[get_current_user] = override_get_current_user

        payload = {"emails": ["newuser@example.com"], "role": "member"}

        response = await client.post(
            f"/api/workspaces/{test_workspace.id}/invitations", json=payload
        )

        assert response.status_code == 403

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_create_invitations_invalid_email(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_workspace: Workspace,
        test_user: User,
        admin_member: WorkspaceMember,
    ):
        """Test that invalid emails are rejected."""
        # Mock authentication
        from app.api.dependencies import get_current_user

        async def override_get_current_user():
            return test_user

        from app.main import app

        app.dependency_overrides[get_current_user] = override_get_current_user

        payload = {"emails": ["invalid-email"], "role": "member"}

        response = await client.post(
            f"/api/workspaces/{test_workspace.id}/invitations", json=payload
        )

        assert response.status_code == 422  # Validation error

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_create_invitations_max_limit(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_workspace: Workspace,
        test_user: User,
        admin_member: WorkspaceMember,
    ):
        """Test that max 10 emails limit is enforced."""
        # Mock authentication
        from app.api.dependencies import get_current_user

        async def override_get_current_user():
            return test_user

        from app.main import app

        app.dependency_overrides[get_current_user] = override_get_current_user

        # Try to invite 11 users
        emails = [f"user{i}@example.com" for i in range(11)]
        payload = {"emails": emails, "role": "member"}

        response = await client.post(
            f"/api/workspaces/{test_workspace.id}/invitations", json=payload
        )

        assert response.status_code == 422  # Validation error

        app.dependency_overrides.clear()


class TestGetInvitations:
    """Tests for GET /api/workspaces/{workspace_id}/invitations"""

    @pytest.mark.asyncio
    async def test_get_pending_invitations_as_admin(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_workspace: Workspace,
        test_user: User,
        admin_member: WorkspaceMember,
    ):
        """Test that admin can view pending invitations."""
        # Create test invitations
        invitation1 = WorkspaceInvitation(
            id=uuid.uuid4(),
            workspace_id=test_workspace.id,
            email="pending1@example.com",
            token="token1",
            role=RoleEnum.MEMBER,
            invited_by=test_user.id,
            expires_at=datetime.utcnow() + timedelta(days=7),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        invitation2 = WorkspaceInvitation(
            id=uuid.uuid4(),
            workspace_id=test_workspace.id,
            email="pending2@example.com",
            token="token2",
            role=RoleEnum.ADMIN,
            invited_by=test_user.id,
            expires_at=datetime.utcnow() + timedelta(days=7),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db_session.add_all([invitation1, invitation2])
        await db_session.commit()

        # Mock authentication
        from app.api.dependencies import get_current_user

        async def override_get_current_user():
            return test_user

        from app.main import app

        app.dependency_overrides[get_current_user] = override_get_current_user

        response = await client.get(f"/api/workspaces/{test_workspace.id}/invitations")

        assert response.status_code == 200
        data = response.json()

        assert len(data) == 2
        emails = [inv["email"] for inv in data]
        assert "pending1@example.com" in emails
        assert "pending2@example.com" in emails

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_invitations_as_member_forbidden(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_workspace: Workspace,
        regular_member: tuple[WorkspaceMember, User],
    ):
        """Test that regular members cannot view invitations."""
        _, regular_user = regular_member

        # Mock authentication
        from app.api.dependencies import get_current_user

        async def override_get_current_user():
            return regular_user

        from app.main import app

        app.dependency_overrides[get_current_user] = override_get_current_user

        response = await client.get(f"/api/workspaces/{test_workspace.id}/invitations")

        assert response.status_code == 403

        app.dependency_overrides.clear()


class TestGetInvitationByToken:
    """Tests for GET /api/invitations/{token}"""

    @pytest.mark.asyncio
    async def test_get_invitation_details_valid_token(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_workspace: Workspace,
        test_user: User,
    ):
        """Test getting invitation details with valid token."""
        invitation = WorkspaceInvitation(
            id=uuid.uuid4(),
            workspace_id=test_workspace.id,
            email="invitee@example.com",
            token="valid_token_123",
            role=RoleEnum.MEMBER,
            invited_by=test_user.id,
            expires_at=datetime.utcnow() + timedelta(days=7),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db_session.add(invitation)
        await db_session.commit()

        response = await client.get("/api/invitations/valid_token_123")

        assert response.status_code == 200
        data = response.json()

        assert data["email"] == "invitee@example.com"
        assert data["workspace_name"] == "Test Workspace"
        assert data["role"] == "member"
        assert "expires_at" in data

    @pytest.mark.asyncio
    async def test_get_invitation_details_invalid_token(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test getting invitation details with invalid token."""
        response = await client.get("/api/invitations/invalid_token_xyz")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_invitation_details_expired_token(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_workspace: Workspace,
        test_user: User,
    ):
        """Test getting invitation details with expired token."""
        invitation = WorkspaceInvitation(
            id=uuid.uuid4(),
            workspace_id=test_workspace.id,
            email="invitee@example.com",
            token="expired_token",
            role=RoleEnum.MEMBER,
            invited_by=test_user.id,
            expires_at=datetime.utcnow() - timedelta(days=1),  # Expired
            created_at=datetime.utcnow() - timedelta(days=8),
            updated_at=datetime.utcnow() - timedelta(days=8),
        )
        db_session.add(invitation)
        await db_session.commit()

        response = await client.get("/api/invitations/expired_token")

        assert response.status_code == 400
        assert "expired" in response.json()["detail"].lower()


class TestAcceptInvitation:
    """Tests for POST /api/invitations/{token}/accept"""

    @pytest.mark.asyncio
    async def test_accept_invitation_success(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_workspace: Workspace,
    ):
        """Test successfully accepting an invitation."""
        # Create user who will accept
        acceptor = User(
            github_id=11111,
            username="acceptor",
            email="acceptor@example.com",
        )
        db_session.add(acceptor)
        await db_session.flush()

        # Create invitation for this user
        invitation = WorkspaceInvitation(
            id=uuid.uuid4(),
            workspace_id=test_workspace.id,
            email="acceptor@example.com",
            token="accept_token",
            role=RoleEnum.MEMBER,
            invited_by=uuid.uuid4(),
            expires_at=datetime.utcnow() + timedelta(days=7),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db_session.add(invitation)
        await db_session.commit()

        # Mock authentication
        from app.api.dependencies import get_current_user

        async def override_get_current_user():
            return acceptor

        from app.main import app

        app.dependency_overrides[get_current_user] = override_get_current_user

        response = await client.post("/api/invitations/accept_token/accept")

        assert response.status_code == 200
        data = response.json()

        assert data["workspace_id"] == str(test_workspace.id)
        assert "message" in data

        # Verify membership was created
        result = await db_session.execute(
            select(WorkspaceMember).where(
                WorkspaceMember.workspace_id == test_workspace.id,
                WorkspaceMember.user_id == acceptor.id,
            )
        )
        member = result.scalar_one_or_none()
        assert member is not None
        assert member.role == RoleEnum.MEMBER

        # Verify invitation was marked as accepted
        await db_session.refresh(invitation)
        assert invitation.accepted_at is not None
        assert invitation.accepted_by == acceptor.id

        # Verify audit log
        result = await db_session.execute(
            select(WorkspaceAuditLog).where(
                WorkspaceAuditLog.workspace_id == test_workspace.id,
                WorkspaceAuditLog.actor_id == acceptor.id,
            )
        )
        audit_log = result.scalar_one_or_none()
        assert audit_log is not None

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_accept_invitation_email_mismatch(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_workspace: Workspace,
    ):
        """Test accepting invitation with wrong email."""
        # Create user with different email
        wrong_user = User(
            github_id=22222,
            username="wronguser",
            email="wrong@example.com",
        )
        db_session.add(wrong_user)
        await db_session.flush()

        # Create invitation for different email
        invitation = WorkspaceInvitation(
            id=uuid.uuid4(),
            workspace_id=test_workspace.id,
            email="correct@example.com",
            token="mismatch_token",
            role=RoleEnum.MEMBER,
            invited_by=uuid.uuid4(),
            expires_at=datetime.utcnow() + timedelta(days=7),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db_session.add(invitation)
        await db_session.commit()

        # Mock authentication
        from app.api.dependencies import get_current_user

        async def override_get_current_user():
            return wrong_user

        from app.main import app

        app.dependency_overrides[get_current_user] = override_get_current_user

        response = await client.post("/api/invitations/mismatch_token/accept")

        assert response.status_code == 400
        data = response.json()

        # Check for email mismatch error with details
        assert "email_mismatch" in data["detail"]["type"]
        assert data["detail"]["invitation_email"] == "correct@example.com"
        assert data["detail"]["user_email"] == "wrong@example.com"

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_accept_invitation_already_member(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_workspace: Workspace,
    ):
        """Test accepting invitation when already a member."""
        # Create user
        existing_user = User(
            github_id=33333,
            username="existing",
            email="existing@example.com",
        )
        db_session.add(existing_user)
        await db_session.flush()

        # User is already a member
        existing_member = WorkspaceMember(
            workspace_id=test_workspace.id,
            user_id=existing_user.id,
            role=RoleEnum.MEMBER,
            joined_at=datetime.utcnow(),
        )
        db_session.add(existing_member)

        # Create invitation
        invitation = WorkspaceInvitation(
            id=uuid.uuid4(),
            workspace_id=test_workspace.id,
            email="existing@example.com",
            token="already_member_token",
            role=RoleEnum.MEMBER,
            invited_by=uuid.uuid4(),
            expires_at=datetime.utcnow() + timedelta(days=7),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db_session.add(invitation)
        await db_session.commit()

        # Mock authentication
        from app.api.dependencies import get_current_user

        async def override_get_current_user():
            return existing_user

        from app.main import app

        app.dependency_overrides[get_current_user] = override_get_current_user

        response = await client.post("/api/invitations/already_member_token/accept")

        assert response.status_code == 400
        assert "already a member" in response.json()["detail"].lower()

        app.dependency_overrides.clear()


class TestRevokeInvitation:
    """Tests for DELETE /api/workspaces/{workspace_id}/invitations/{invitation_id}"""

    @pytest.mark.asyncio
    async def test_revoke_invitation_as_admin(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_workspace: Workspace,
        test_user: User,
        admin_member: WorkspaceMember,
    ):
        """Test that admin can revoke invitations."""
        # Create invitation
        invitation = WorkspaceInvitation(
            id=uuid.uuid4(),
            workspace_id=test_workspace.id,
            email="revoke@example.com",
            token="revoke_token",
            role=RoleEnum.MEMBER,
            invited_by=test_user.id,
            expires_at=datetime.utcnow() + timedelta(days=7),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db_session.add(invitation)
        await db_session.commit()

        # Mock authentication
        from app.api.dependencies import get_current_user

        async def override_get_current_user():
            return test_user

        from app.main import app

        app.dependency_overrides[get_current_user] = override_get_current_user

        response = await client.delete(
            f"/api/workspaces/{test_workspace.id}/invitations/{invitation.id}"
        )

        assert response.status_code == 204

        # Verify invitation was deleted
        result = await db_session.execute(
            select(WorkspaceInvitation).where(WorkspaceInvitation.id == invitation.id)
        )
        deleted_invitation = result.scalar_one_or_none()
        assert deleted_invitation is None

        # Verify audit log
        result = await db_session.execute(
            select(WorkspaceAuditLog).where(WorkspaceAuditLog.workspace_id == test_workspace.id)
        )
        audit_logs = result.scalars().all()
        assert len(audit_logs) > 0

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_revoke_invitation_as_member_forbidden(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_workspace: Workspace,
        test_user: User,
        regular_member: tuple[WorkspaceMember, User],
    ):
        """Test that regular members cannot revoke invitations."""
        _, regular_user = regular_member

        # Create invitation
        invitation = WorkspaceInvitation(
            id=uuid.uuid4(),
            workspace_id=test_workspace.id,
            email="revoke@example.com",
            token="revoke_token",
            role=RoleEnum.MEMBER,
            invited_by=test_user.id,
            expires_at=datetime.utcnow() + timedelta(days=7),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db_session.add(invitation)
        await db_session.commit()

        # Mock authentication
        from app.api.dependencies import get_current_user

        async def override_get_current_user():
            return regular_user

        from app.main import app

        app.dependency_overrides[get_current_user] = override_get_current_user

        response = await client.delete(
            f"/api/workspaces/{test_workspace.id}/invitations/{invitation.id}"
        )

        assert response.status_code == 403

        app.dependency_overrides.clear()


class TestResendInvitation:
    """Tests for POST /api/workspaces/{workspace_id}/invitations/{invitation_id}/resend"""

    @pytest.mark.asyncio
    async def test_resend_invitation_as_admin(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_workspace: Workspace,
        test_user: User,
        admin_member: WorkspaceMember,
    ):
        """Test that admin can resend invitations."""
        # Create invitation
        old_token = "old_token"
        invitation = WorkspaceInvitation(
            id=uuid.uuid4(),
            workspace_id=test_workspace.id,
            email="resend@example.com",
            token=old_token,
            role=RoleEnum.MEMBER,
            invited_by=test_user.id,
            expires_at=datetime.utcnow() + timedelta(days=1),
            created_at=datetime.utcnow() - timedelta(days=6),
            updated_at=datetime.utcnow() - timedelta(days=6),
        )
        db_session.add(invitation)
        await db_session.commit()

        # Mock authentication
        from app.api.dependencies import get_current_user

        async def override_get_current_user():
            return test_user

        from app.main import app

        app.dependency_overrides[get_current_user] = override_get_current_user

        response = await client.post(
            f"/api/workspaces/{test_workspace.id}/invitations/{invitation.id}/resend"
        )

        assert response.status_code == 200
        data = response.json()

        # Token should be refreshed
        await db_session.refresh(invitation)
        assert invitation.token != old_token

        # Expiration should be extended
        assert invitation.expires_at > datetime.utcnow() + timedelta(days=6)

        # Verify audit log
        result = await db_session.execute(
            select(WorkspaceAuditLog).where(WorkspaceAuditLog.workspace_id == test_workspace.id)
        )
        audit_logs = result.scalars().all()
        assert len(audit_logs) > 0

        app.dependency_overrides.clear()


class TestCascadeDelete:
    """Tests for cascade deletion of invitations."""

    @pytest.mark.asyncio
    async def test_deleting_workspace_cascades_to_invitations(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_workspace: Workspace,
        test_user: User,
        admin_member: WorkspaceMember,
    ):
        """Test that deleting workspace also deletes pending invitations."""
        # Create some pending invitations
        invitation1 = WorkspaceInvitation(
            id=uuid.uuid4(),
            workspace_id=test_workspace.id,
            email="pending1@example.com",
            token="cascade_token1",
            role=RoleEnum.MEMBER,
            invited_by=test_user.id,
            expires_at=datetime.utcnow() + timedelta(days=7),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        invitation2 = WorkspaceInvitation(
            id=uuid.uuid4(),
            workspace_id=test_workspace.id,
            email="pending2@example.com",
            token="cascade_token2",
            role=RoleEnum.MEMBER,
            invited_by=test_user.id,
            expires_at=datetime.utcnow() + timedelta(days=7),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db_session.add_all([invitation1, invitation2])
        await db_session.commit()

        # Verify invitations exist
        result = await db_session.execute(
            select(WorkspaceInvitation).where(
                WorkspaceInvitation.workspace_id == test_workspace.id
            )
        )
        invitations_before = result.scalars().all()
        assert len(invitations_before) == 2

        # Mock authentication
        from app.api.dependencies import get_current_user

        async def override_get_current_user():
            return test_user

        from app.main import app

        app.dependency_overrides[get_current_user] = override_get_current_user

        # Delete workspace
        response = await client.delete(f"/api/workspaces/{test_workspace.id}")

        assert response.status_code == 204

        # Verify invitations were cascade deleted
        result = await db_session.execute(
            select(WorkspaceInvitation).where(
                WorkspaceInvitation.workspace_id == test_workspace.id
            )
        )
        invitations_after = result.scalars().all()
        assert len(invitations_after) == 0

        # Verify workspace was deleted
        result = await db_session.execute(
            select(Workspace).where(Workspace.id == test_workspace.id)
        )
        workspace = result.scalar_one_or_none()
        assert workspace is None

        app.dependency_overrides.clear()


class TestRateLimiting:
    """Tests for rate limiting on invitation creation.
    
    NOTE: Rate limiting is not yet implemented. These tests document the expected behavior.
    """

    @pytest.mark.skip(reason="Rate limiting not yet implemented")
    @pytest.mark.asyncio
    async def test_rate_limiting_blocks_excessive_invitations(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_workspace: Workspace,
        test_user: User,
        admin_member: WorkspaceMember,
    ):
        """
        Test that rate limiting prevents more than 50 invitations per hour.
        
        Expected behavior:
        - First 50 invitation requests succeed (201)
        - 51st request returns 429 Too Many Requests
        - Response includes Retry-After header
        - Rate limit resets after 1 hour
        
        TODO: Implement rate limiting using:
        - Redis for distributed rate limiting
        - Sliding window algorithm
        - Per-workspace or per-user limits
        - Configuration in settings
        
        Implementation location: app/api/invitations.py
        Add rate limiting middleware or dependency
        """
        from app.api.dependencies import get_current_user
        from app.main import app

        async def override_get_current_user():
            return test_user

        app.dependency_overrides[get_current_user] = override_get_current_user

        # Send 50 invitations (should all succeed)
        for i in range(50):
            response = await client.post(
                f"/api/workspaces/{test_workspace.id}/invitations",
                json={"emails": [f"user{i}@example.com"], "role": "member"},
            )
            assert response.status_code == 201, f"Invitation {i+1} should succeed"

        # 51st invitation should be rate limited
        response = await client.post(
            f"/api/workspaces/{test_workspace.id}/invitations",
            json={"emails": ["blocked@example.com"], "role": "member"},
        )
        assert response.status_code == 429, "Should return 429 Too Many Requests"
        assert "Retry-After" in response.headers
        
        error_data = response.json()
        assert "rate limit" in error_data["detail"].lower()

        app.dependency_overrides.clear()

    @pytest.mark.skip(reason="Rate limiting not yet implemented")
    @pytest.mark.asyncio
    async def test_rate_limit_is_per_workspace(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user: User,
    ):
        """
        Test that rate limits are per-workspace, not global.
        
        A user should be able to send 50 invitations to Workspace A
        and 50 invitations to Workspace B within the same hour.
        """
        pass

    @pytest.mark.skip(reason="Rate limiting not yet implemented")
    @pytest.mark.asyncio
    async def test_rate_limit_resets_after_window(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_workspace: Workspace,
        test_user: User,
        admin_member: WorkspaceMember,
    ):
        """
        Test that rate limit resets after the time window expires.
        
        TODO: Implement using time-based testing or mocked time
        """
        pass

    @pytest.mark.skip(reason="Rate limiting not yet implemented")
    @pytest.mark.asyncio
    async def test_rate_limit_counts_all_emails_in_batch(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_workspace: Workspace,
        test_user: User,
        admin_member: WorkspaceMember,
    ):
        """
        Test that rate limiting counts individual emails, not API requests.
        
        Sending one request with 10 emails should count as 10 toward the limit.
        """
        pass


# Implementation Checklist for Rate Limiting:
#
# [ ] Add Redis dependency for distributed rate limiting
# [ ] Create rate limiting middleware or dependency
# [ ] Configure rate limits in settings (default: 50/hour)
# [ ] Implement sliding window algorithm
# [ ] Add rate limit headers to responses:
#     - X-RateLimit-Limit: 50
#     - X-RateLimit-Remaining: 23
#     - X-RateLimit-Reset: 1234567890
#     - Retry-After: 3600 (when limit exceeded)
# [ ] Make rate limits configurable per environment
# [ ] Add rate limit bypass for admin/system users
# [ ] Log rate limit violations for monitoring
# [ ] Update API documentation with rate limit info

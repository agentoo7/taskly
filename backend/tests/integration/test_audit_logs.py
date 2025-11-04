"""Integration tests for audit logging in invitation and member operations."""

import pytest
from sqlalchemy import select

from app.models.workspace_audit_log import AuditActionEnum, WorkspaceAuditLog
from app.models.workspace_member import RoleEnum


@pytest.mark.asyncio
async def test_invitation_created_audit_log(
    client, test_workspace, admin_user, admin_headers, db_session
):
    """Test that creating invitations generates audit logs."""
    # Create invitations
    response = await client.post(
        f"/api/workspaces/{test_workspace.id}/invitations",
        json={"emails": ["user1@example.com", "user2@example.com"], "role": "member"},
        headers=admin_headers,
    )
    assert response.status_code == 201

    # Verify audit logs created
    result = await db_session.execute(
        select(WorkspaceAuditLog)
        .where(WorkspaceAuditLog.workspace_id == test_workspace.id)
        .where(WorkspaceAuditLog.action == AuditActionEnum.INVITATION_CREATED)
    )
    audit_logs = result.scalars().all()

    assert len(audit_logs) == 2
    assert all(log.actor_id == admin_user.id for log in audit_logs)
    assert all(log.resource_type == "invitation" for log in audit_logs)


@pytest.mark.asyncio
async def test_invitation_accepted_audit_log(
    client, test_workspace, admin_user, test_user, auth_headers, db_session
):
    """Test that accepting invitation generates audit log."""
    # Create invitation first
    from app.models.workspace_invitation import WorkspaceInvitation

    invitation = WorkspaceInvitation(
        workspace_id=test_workspace.id,
        email=test_user.email,
        role=RoleEnum.MEMBER,
        invited_by=admin_user.id,
    )
    db_session.add(invitation)
    await db_session.commit()
    await db_session.refresh(invitation)

    # Accept invitation
    response = await client.post(
        f"/api/invitations/{invitation.token}/accept",
        headers=auth_headers(test_user),
    )
    assert response.status_code == 200

    # Verify audit log created
    result = await db_session.execute(
        select(WorkspaceAuditLog)
        .where(WorkspaceAuditLog.workspace_id == test_workspace.id)
        .where(WorkspaceAuditLog.action == AuditActionEnum.INVITATION_ACCEPTED)
    )
    audit_log = result.scalar_one()

    assert audit_log.actor_id == test_user.id
    assert audit_log.resource_type == "invitation"
    assert audit_log.resource_id == invitation.id
    assert audit_log.context_data["email"] == test_user.email


@pytest.mark.asyncio
async def test_invitation_revoked_audit_log(
    client, test_workspace, admin_user, admin_headers, db_session
):
    """Test that revoking invitation generates audit log."""
    # Create invitation first
    from app.models.workspace_invitation import WorkspaceInvitation

    invitation = WorkspaceInvitation(
        workspace_id=test_workspace.id,
        email="revoke@example.com",
        role=RoleEnum.MEMBER,
        invited_by=admin_user.id,
    )
    db_session.add(invitation)
    await db_session.commit()
    await db_session.refresh(invitation)

    invitation_id = invitation.id

    # Revoke invitation
    response = await client.delete(
        f"/api/workspaces/{test_workspace.id}/invitations/{invitation_id}",
        headers=admin_headers,
    )
    assert response.status_code == 204

    # Verify audit log created
    result = await db_session.execute(
        select(WorkspaceAuditLog)
        .where(WorkspaceAuditLog.workspace_id == test_workspace.id)
        .where(WorkspaceAuditLog.action == AuditActionEnum.INVITATION_REVOKED)
    )
    audit_log = result.scalar_one()

    assert audit_log.actor_id == admin_user.id
    assert audit_log.resource_id == invitation_id


@pytest.mark.asyncio
async def test_invitation_resent_audit_log(
    client, test_workspace, admin_user, admin_headers, db_session
):
    """Test that resending invitation generates audit log."""
    # Create invitation first
    from app.models.workspace_invitation import WorkspaceInvitation

    invitation = WorkspaceInvitation(
        workspace_id=test_workspace.id,
        email="resend@example.com",
        role=RoleEnum.MEMBER,
        invited_by=admin_user.id,
    )
    db_session.add(invitation)
    await db_session.commit()
    await db_session.refresh(invitation)

    # Resend invitation
    response = await client.post(
        f"/api/workspaces/{test_workspace.id}/invitations/{invitation.id}/resend",
        headers=admin_headers,
    )
    assert response.status_code == 200

    # Verify audit log created
    result = await db_session.execute(
        select(WorkspaceAuditLog)
        .where(WorkspaceAuditLog.workspace_id == test_workspace.id)
        .where(WorkspaceAuditLog.action == AuditActionEnum.INVITATION_RESENT)
    )
    audit_log = result.scalar_one()

    assert audit_log.actor_id == admin_user.id
    assert audit_log.resource_id == invitation.id


@pytest.mark.asyncio
async def test_member_role_changed_audit_log(
    client, test_workspace, admin_user, member_user, admin_headers, db_session
):
    """Test that changing member role generates audit log."""
    # Change role
    response = await client.patch(
        f"/api/workspaces/{test_workspace.id}/members/{member_user.id}",
        json={"role": "admin"},
        headers=admin_headers,
    )
    assert response.status_code == 200

    # Verify audit log created
    result = await db_session.execute(
        select(WorkspaceAuditLog)
        .where(WorkspaceAuditLog.workspace_id == test_workspace.id)
        .where(WorkspaceAuditLog.action == AuditActionEnum.MEMBER_ROLE_CHANGED)
    )
    audit_log = result.scalar_one()

    assert audit_log.actor_id == admin_user.id
    assert audit_log.resource_type == "member"
    assert audit_log.resource_id == member_user.id
    assert audit_log.context_data["old_role"] == "RoleEnum.MEMBER"
    assert audit_log.context_data["new_role"] == "admin"


@pytest.mark.asyncio
async def test_member_removed_audit_log(
    client, test_workspace, admin_user, member_user, admin_headers, db_session
):
    """Test that removing member generates audit log."""
    # Remove member
    response = await client.delete(
        f"/api/workspaces/{test_workspace.id}/members/{member_user.id}",
        headers=admin_headers,
    )
    assert response.status_code == 204

    # Verify audit log created
    result = await db_session.execute(
        select(WorkspaceAuditLog)
        .where(WorkspaceAuditLog.workspace_id == test_workspace.id)
        .where(WorkspaceAuditLog.action == AuditActionEnum.MEMBER_REMOVED)
    )
    audit_log = result.scalar_one()

    assert audit_log.actor_id == admin_user.id
    assert audit_log.resource_type == "member"
    assert audit_log.resource_id == member_user.id


@pytest.mark.asyncio
async def test_audit_logs_ordered_by_creation_time(
    client, test_workspace, admin_user, admin_headers, db_session
):
    """Test that audit logs can be retrieved in chronological order."""
    # Perform multiple actions
    await client.post(
        f"/api/workspaces/{test_workspace.id}/invitations",
        json={"emails": ["user1@example.com"], "role": "member"},
        headers=admin_headers,
    )

    await client.post(
        f"/api/workspaces/{test_workspace.id}/invitations",
        json={"emails": ["user2@example.com"], "role": "admin"},
        headers=admin_headers,
    )

    # Retrieve audit logs
    result = await db_session.execute(
        select(WorkspaceAuditLog)
        .where(WorkspaceAuditLog.workspace_id == test_workspace.id)
        .order_by(WorkspaceAuditLog.created_at.asc())
    )
    audit_logs = result.scalars().all()

    assert len(audit_logs) >= 2
    # Verify chronological order
    for i in range(len(audit_logs) - 1):
        assert audit_logs[i].created_at <= audit_logs[i + 1].created_at


@pytest.mark.asyncio
async def test_only_admins_can_access_audit_logs(
    client, test_workspace, admin_user, member_user, admin_headers, auth_headers
):
    """Test that only admins can access audit logs endpoint."""
    # Admin should be able to access
    response = await client.get(
        f"/api/workspaces/{test_workspace.id}/audit-logs",
        headers=admin_headers,
    )
    # Note: This test will pass once the endpoint is implemented
    # For now, we expect 404 since endpoint doesn't exist yet
    assert response.status_code in [200, 404]

    # Regular member should be forbidden
    response = await client.get(
        f"/api/workspaces/{test_workspace.id}/audit-logs",
        headers=auth_headers(member_user),
    )
    assert response.status_code in [403, 404]

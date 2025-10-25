"""Tests for cleanup_invitations Celery task."""

import uuid
from datetime import datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workspace_invitation import WorkspaceInvitation
from app.models.workspace_member import RoleEnum
from app.tasks.cleanup_invitations import _cleanup_expired_invitations


@pytest.mark.asyncio
async def test_cleanup_deletes_expired_invitations_older_than_30_days(
    db_session: AsyncSession,
):
    """Test that cleanup job deletes expired invitations older than 30 days."""
    # Create expired invitation older than 30 days (should be deleted)
    old_expired = WorkspaceInvitation(
        id=uuid.uuid4(),
        workspace_id=uuid.uuid4(),
        email="old_expired@example.com",
        token="old_expired_token",
        role=RoleEnum.MEMBER,
        invited_by=uuid.uuid4(),
        expires_at=datetime.utcnow() - timedelta(days=40),  # Expired 40 days ago
        created_at=datetime.utcnow() - timedelta(days=47),
        updated_at=datetime.utcnow() - timedelta(days=47),
    )
    db_session.add(old_expired)
    await db_session.commit()

    # Run cleanup
    result = await _cleanup_expired_invitations()

    # Verify old expired invitation was deleted
    assert result["deleted_count"] == 1

    # Verify in database
    stmt = select(WorkspaceInvitation).where(WorkspaceInvitation.id == old_expired.id)
    result_db = await db_session.execute(stmt)
    invitation = result_db.scalar_one_or_none()
    assert invitation is None


@pytest.mark.asyncio
async def test_cleanup_does_not_delete_recent_expired_invitations(
    db_session: AsyncSession,
):
    """Test that cleanup job does not delete expired invitations less than 30 days old."""
    # Create recently expired invitation (should NOT be deleted)
    recent_expired = WorkspaceInvitation(
        id=uuid.uuid4(),
        workspace_id=uuid.uuid4(),
        email="recent_expired@example.com",
        token="recent_expired_token",
        role=RoleEnum.MEMBER,
        invited_by=uuid.uuid4(),
        expires_at=datetime.utcnow() - timedelta(days=10),  # Expired 10 days ago
        created_at=datetime.utcnow() - timedelta(days=17),
        updated_at=datetime.utcnow() - timedelta(days=17),
    )
    db_session.add(recent_expired)
    await db_session.commit()

    # Run cleanup
    result = await _cleanup_expired_invitations()

    # Verify nothing was deleted
    assert result["deleted_count"] == 0

    # Verify invitation still exists in database
    stmt = select(WorkspaceInvitation).where(WorkspaceInvitation.id == recent_expired.id)
    result_db = await db_session.execute(stmt)
    invitation = result_db.scalar_one_or_none()
    assert invitation is not None


@pytest.mark.asyncio
async def test_cleanup_does_not_delete_accepted_invitations(
    db_session: AsyncSession,
):
    """Test that cleanup job does not delete accepted invitations."""
    # Create old expired but accepted invitation (should NOT be deleted)
    accepted_invitation = WorkspaceInvitation(
        id=uuid.uuid4(),
        workspace_id=uuid.uuid4(),
        email="accepted@example.com",
        token="accepted_token",
        role=RoleEnum.MEMBER,
        invited_by=uuid.uuid4(),
        expires_at=datetime.utcnow() - timedelta(days=40),  # Expired 40 days ago
        accepted_at=datetime.utcnow() - timedelta(days=35),  # But was accepted
        accepted_by=uuid.uuid4(),
        created_at=datetime.utcnow() - timedelta(days=47),
        updated_at=datetime.utcnow() - timedelta(days=35),
    )
    db_session.add(accepted_invitation)
    await db_session.commit()

    # Run cleanup
    result = await _cleanup_expired_invitations()

    # Verify nothing was deleted (accepted invitations are preserved)
    assert result["deleted_count"] == 0

    # Verify invitation still exists in database
    stmt = select(WorkspaceInvitation).where(
        WorkspaceInvitation.id == accepted_invitation.id
    )
    result_db = await db_session.execute(stmt)
    invitation = result_db.scalar_one_or_none()
    assert invitation is not None


@pytest.mark.asyncio
async def test_cleanup_does_not_delete_valid_invitations(
    db_session: AsyncSession,
):
    """Test that cleanup job does not delete valid (not expired) invitations."""
    # Create valid invitation (should NOT be deleted)
    valid_invitation = WorkspaceInvitation(
        id=uuid.uuid4(),
        workspace_id=uuid.uuid4(),
        email="valid@example.com",
        token="valid_token",
        role=RoleEnum.MEMBER,
        invited_by=uuid.uuid4(),
        expires_at=datetime.utcnow() + timedelta(days=5),  # Still valid
        created_at=datetime.utcnow() - timedelta(days=2),
        updated_at=datetime.utcnow() - timedelta(days=2),
    )
    db_session.add(valid_invitation)
    await db_session.commit()

    # Run cleanup
    result = await _cleanup_expired_invitations()

    # Verify nothing was deleted
    assert result["deleted_count"] == 0

    # Verify invitation still exists in database
    stmt = select(WorkspaceInvitation).where(
        WorkspaceInvitation.id == valid_invitation.id
    )
    result_db = await db_session.execute(stmt)
    invitation = result_db.scalar_one_or_none()
    assert invitation is not None


@pytest.mark.asyncio
async def test_cleanup_deletes_multiple_old_expired_invitations(
    db_session: AsyncSession,
):
    """Test that cleanup job deletes multiple old expired invitations."""
    # Create multiple old expired invitations (all should be deleted)
    invitations = []
    for i in range(5):
        invitation = WorkspaceInvitation(
            id=uuid.uuid4(),
            workspace_id=uuid.uuid4(),
            email=f"old_expired_{i}@example.com",
            token=f"old_expired_token_{i}",
            role=RoleEnum.MEMBER,
            invited_by=uuid.uuid4(),
            expires_at=datetime.utcnow() - timedelta(days=35 + i),
            created_at=datetime.utcnow() - timedelta(days=42 + i),
            updated_at=datetime.utcnow() - timedelta(days=42 + i),
        )
        invitations.append(invitation)
        db_session.add(invitation)

    # Create one recent expired invitation (should NOT be deleted)
    recent = WorkspaceInvitation(
        id=uuid.uuid4(),
        workspace_id=uuid.uuid4(),
        email="recent@example.com",
        token="recent_token",
        role=RoleEnum.MEMBER,
        invited_by=uuid.uuid4(),
        expires_at=datetime.utcnow() - timedelta(days=10),
        created_at=datetime.utcnow() - timedelta(days=17),
        updated_at=datetime.utcnow() - timedelta(days=17),
    )
    db_session.add(recent)
    await db_session.commit()

    # Run cleanup
    result = await _cleanup_expired_invitations()

    # Verify only 5 old invitations were deleted
    assert result["deleted_count"] == 5

    # Verify old invitations are gone
    for invitation in invitations:
        stmt = select(WorkspaceInvitation).where(WorkspaceInvitation.id == invitation.id)
        result_db = await db_session.execute(stmt)
        found = result_db.scalar_one_or_none()
        assert found is None, f"Invitation {invitation.email} should have been deleted"

    # Verify recent invitation still exists
    stmt = select(WorkspaceInvitation).where(WorkspaceInvitation.id == recent.id)
    result_db = await db_session.execute(stmt)
    found = result_db.scalar_one_or_none()
    assert found is not None, "Recent invitation should not have been deleted"

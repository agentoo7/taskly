"""Unit tests for AuditService."""

import uuid
from datetime import datetime

import pytest
from sqlalchemy import select

from app.models.workspace_audit_log import AuditActionEnum, WorkspaceAuditLog
from app.services.audit_service import AuditService


@pytest.mark.asyncio
async def test_log_action_creates_audit_entry(db_session):
    """Test that log_action creates an audit log entry."""
    service = AuditService(db_session)

    workspace_id = uuid.uuid4()
    actor_id = uuid.uuid4()
    resource_id = uuid.uuid4()

    # Log an action
    log_entry = await service.log_action(
        workspace_id=workspace_id,
        actor_id=actor_id,
        action=AuditActionEnum.INVITATION_CREATED,
        resource_type="invitation",
        resource_id=resource_id,
        context_data={"email": "test@example.com", "role": "member"},
    )

    # Verify entry was created
    assert log_entry.id is not None
    assert log_entry.workspace_id == workspace_id
    assert log_entry.actor_id == actor_id
    assert log_entry.action == AuditActionEnum.INVITATION_CREATED
    assert log_entry.resource_type == "invitation"
    assert log_entry.resource_id == resource_id
    assert log_entry.context_data == {"email": "test@example.com", "role": "member"}
    assert isinstance(log_entry.created_at, datetime)


@pytest.mark.asyncio
async def test_log_action_persists_to_database(db_session):
    """Test that logged actions are persisted to database."""
    service = AuditService(db_session)

    workspace_id = uuid.uuid4()
    actor_id = uuid.uuid4()
    resource_id = uuid.uuid4()

    # Log an action
    log_entry = await service.log_action(
        workspace_id=workspace_id,
        actor_id=actor_id,
        action=AuditActionEnum.MEMBER_ROLE_CHANGED,
        resource_type="member",
        resource_id=resource_id,
        context_data={"old_role": "member", "new_role": "admin"},
    )

    # Query database directly
    result = await db_session.execute(
        select(WorkspaceAuditLog).where(WorkspaceAuditLog.id == log_entry.id)
    )
    retrieved_entry = result.scalar_one()

    assert retrieved_entry.id == log_entry.id
    assert retrieved_entry.workspace_id == workspace_id
    assert retrieved_entry.action == AuditActionEnum.MEMBER_ROLE_CHANGED


@pytest.mark.asyncio
async def test_log_action_with_null_context_data(db_session):
    """Test that log_action works without context_data."""
    service = AuditService(db_session)

    workspace_id = uuid.uuid4()
    actor_id = uuid.uuid4()
    resource_id = uuid.uuid4()

    # Log action without context_data
    log_entry = await service.log_action(
        workspace_id=workspace_id,
        actor_id=actor_id,
        action=AuditActionEnum.INVITATION_REVOKED,
        resource_type="invitation",
        resource_id=resource_id,
    )

    assert log_entry.context_data == {}


@pytest.mark.asyncio
async def test_log_multiple_actions(db_session):
    """Test logging multiple actions for same workspace."""
    service = AuditService(db_session)

    workspace_id = uuid.uuid4()
    actor_id = uuid.uuid4()

    # Log multiple actions
    actions = [
        AuditActionEnum.INVITATION_CREATED,
        AuditActionEnum.INVITATION_ACCEPTED,
        AuditActionEnum.MEMBER_ROLE_CHANGED,
    ]

    for action in actions:
        await service.log_action(
            workspace_id=workspace_id,
            actor_id=actor_id,
            action=action,
            resource_type="test",
            resource_id=uuid.uuid4(),
        )

    # Query all logs for workspace
    result = await db_session.execute(
        select(WorkspaceAuditLog).where(WorkspaceAuditLog.workspace_id == workspace_id)
    )
    logs = result.scalars().all()

    assert len(logs) == 3
    assert {log.action for log in logs} == set(actions)


@pytest.mark.asyncio
async def test_all_audit_action_enums(db_session):
    """Test that all audit action types can be logged."""
    service = AuditService(db_session)

    workspace_id = uuid.uuid4()
    actor_id = uuid.uuid4()

    all_actions = [
        AuditActionEnum.INVITATION_CREATED,
        AuditActionEnum.INVITATION_ACCEPTED,
        AuditActionEnum.INVITATION_REVOKED,
        AuditActionEnum.INVITATION_RESENT,
        AuditActionEnum.INVITATION_EXPIRED,
        AuditActionEnum.MEMBER_ROLE_CHANGED,
        AuditActionEnum.MEMBER_REMOVED,
    ]

    for action in all_actions:
        log_entry = await service.log_action(
            workspace_id=workspace_id,
            actor_id=actor_id,
            action=action,
            resource_type="test",
            resource_id=uuid.uuid4(),
        )
        assert log_entry.action == action

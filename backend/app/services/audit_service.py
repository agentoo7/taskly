"""Audit service for workspace action logging."""

from uuid import UUID

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workspace_audit_log import AuditActionEnum, WorkspaceAuditLog

logger = structlog.get_logger(__name__)


class AuditService:
    """Service for logging workspace audit events."""

    def __init__(self, db: AsyncSession):
        """
        Initialize AuditService.

        Args:
            db: Async database session
        """
        self.db = db

    async def log_action(
        self,
        workspace_id: UUID,
        actor_id: UUID,
        action: AuditActionEnum,
        resource_type: str,
        resource_id: UUID,
        context_data: dict | None = None,
    ) -> WorkspaceAuditLog:
        """
        Log an audit event for workspace actions.

        Args:
            workspace_id: UUID of workspace
            actor_id: UUID of user performing action
            action: Type of action performed
            resource_type: Type of resource (e.g., "invitation", "member")
            resource_id: UUID of resource affected
            context_data: Additional context (email, role, etc.)

        Returns:
            Created audit log entry
        """
        log_entry = WorkspaceAuditLog(
            workspace_id=workspace_id,
            actor_id=actor_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            context_data=context_data or {},
        )

        self.db.add(log_entry)
        await self.db.commit()
        await self.db.refresh(log_entry)

        logger.info(
            "audit.log.created",
            workspace_id=str(workspace_id),
            actor_id=str(actor_id),
            action=action.value,
            resource_type=resource_type,
            resource_id=str(resource_id),
        )

        return log_entry

    async def get_workspace_audit_logs(
        self,
        workspace_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[WorkspaceAuditLog]:
        """
        Get audit logs for a workspace with pagination.

        Args:
            workspace_id: UUID of workspace
            limit: Maximum number of logs to return
            offset: Number of logs to skip

        Returns:
            List of audit log entries
        """
        result = await self.db.execute(
            select(WorkspaceAuditLog)
            .where(WorkspaceAuditLog.workspace_id == workspace_id)
            .order_by(WorkspaceAuditLog.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        return list(result.scalars().all())

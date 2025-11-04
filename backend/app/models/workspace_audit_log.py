"""WorkspaceAuditLog model for tracking workspace actions."""

import enum
import uuid

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class AuditActionEnum(str, enum.Enum):
    """Audit actions for workspace events."""

    INVITATION_CREATED = "invitation_created"
    INVITATION_ACCEPTED = "invitation_accepted"
    INVITATION_REVOKED = "invitation_revoked"
    INVITATION_RESENT = "invitation_resent"
    INVITATION_EXPIRED = "invitation_expired"
    MEMBER_ROLE_CHANGED = "member_role_changed"
    MEMBER_REMOVED = "member_removed"


class WorkspaceAuditLog(Base):
    """Model for workspace audit trail."""

    __tablename__ = "workspace_audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    actor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    action = Column(Enum(AuditActionEnum), nullable=False)
    resource_type = Column(String(50), nullable=False)  # "invitation", "member"
    resource_id = Column(UUID(as_uuid=True), nullable=False)
    context_data = Column(JSONB, nullable=True)  # Additional context (email, role, etc.)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    workspace = relationship("Workspace")
    actor = relationship("User")

    # Indexes for performance
    __table_args__ = (
        Index("ix_workspace_audit_logs_workspace_id", "workspace_id"),
        Index("ix_workspace_audit_logs_actor_id", "actor_id"),
        Index("ix_workspace_audit_logs_created_at", "created_at"),
        Index("ix_workspace_audit_logs_action", "action"),
    )

    def __repr__(self) -> str:
        """String representation of WorkspaceAuditLog."""
        return f"<WorkspaceAuditLog(workspace_id={self.workspace_id}, action={self.action}, actor_id={self.actor_id})>"

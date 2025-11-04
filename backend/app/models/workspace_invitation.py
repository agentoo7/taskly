"""WorkspaceInvitation model for managing team invitations."""

import enum
import secrets
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.workspace_member import RoleEnum


class DeliveryStatusEnum(str, enum.Enum):
    """Email delivery status tracking."""

    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCED = "bounced"


class WorkspaceInvitation(Base):
    """Model for workspace member invitations."""

    __tablename__ = "workspace_invitations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    email = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False, default=RoleEnum.MEMBER)
    token = Column(
        String(64),
        unique=True,
        nullable=False,
        default=lambda: secrets.token_urlsafe(32),
    )
    invited_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    delivery_status = Column(
        Enum(DeliveryStatusEnum), nullable=False, default=DeliveryStatusEnum.PENDING
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC) + timedelta(days=7),
    )
    accepted_at = Column(DateTime(timezone=True))

    # Relationships
    workspace = relationship("Workspace")
    inviter = relationship("User")

    # Constraints and indexes
    __table_args__ = (
        UniqueConstraint("workspace_id", "email", name="uq_workspace_email_invitation"),
        Index("ix_workspace_invitations_workspace_id", "workspace_id"),
        Index("ix_workspace_invitations_email", "email"),
        Index("ix_workspace_invitations_expires_at", "expires_at"),
    )

    @property
    def is_expired(self) -> bool:
        """Check if invitation has expired."""
        return datetime.now(UTC) > self.expires_at

    @property
    def is_accepted(self) -> bool:
        """Check if invitation has been accepted."""
        return self.accepted_at is not None

    def __repr__(self) -> str:
        """String representation of WorkspaceInvitation."""
        return f"<WorkspaceInvitation(email={self.email}, workspace_id={self.workspace_id}, role={self.role})>"

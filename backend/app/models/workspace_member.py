"""WorkspaceMember join table for workspace membership with roles."""

import enum

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    PrimaryKeyConstraint,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class RoleEnum(str, enum.Enum):
    """Role levels for workspace members."""

    ADMIN = "admin"
    MEMBER = "member"


class WorkspaceMember(Base):
    """Join table for workspace membership with roles."""

    __tablename__ = "workspace_members"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    workspace_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role = Column(Enum(RoleEnum), default=RoleEnum.MEMBER, nullable=False)
    joined_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Composite primary key and unique constraint
    __table_args__ = (
        PrimaryKeyConstraint("user_id", "workspace_id"),
        UniqueConstraint("user_id", "workspace_id", name="uq_workspace_members"),
    )

    def __repr__(self) -> str:
        """String representation of WorkspaceMember."""
        return f"<WorkspaceMember(user_id={self.user_id}, workspace_id={self.workspace_id}, role={self.role})>"

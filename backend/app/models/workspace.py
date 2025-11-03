"""Workspace model for organizing boards and teams."""

import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Workspace(Base):
    """Workspace model representing a top-level organizational container."""

    __tablename__ = "workspaces"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(100), nullable=False)
    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    creator = relationship("User", back_populates="created_workspaces", foreign_keys=[created_by])
    members = relationship(
        "User",
        secondary="workspace_members",
        back_populates="workspaces",
        viewonly=True,
    )
    boards = relationship("Board", back_populates="workspace", cascade="all, delete-orphan")
    labels = relationship(
        "WorkspaceLabel", back_populates="workspace", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation of Workspace."""
        return f"<Workspace(id={self.id}, name={self.name})>"

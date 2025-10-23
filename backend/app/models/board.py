"""Board model for Kanban boards."""

import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Board(Base):
    """Board model representing a Kanban board within a workspace."""

    __tablename__ = "boards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(100), nullable=False)
    columns = Column(
        JSONB, nullable=False, default=list
    )  # [{"id": "uuid", "name": "str", "position": int}]
    archived = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    workspace = relationship("Workspace", back_populates="boards")
    cards = relationship("Card", back_populates="board", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (Index("ix_boards_columns_gin", "columns", postgresql_using="gin"),)

    def __repr__(self) -> str:
        """String representation of Board."""
        return f"<Board(id={self.id}, name={self.name})>"

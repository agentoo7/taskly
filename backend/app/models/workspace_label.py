"""WorkspaceLabel model for label categorization."""

import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class WorkspaceLabel(Base):
    """WorkspaceLabel model representing categorization labels."""

    __tablename__ = "workspace_labels"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(50), nullable=False)
    color = Column(String(7), nullable=False)  # Hex color: #RRGGBB
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    workspace = relationship("Workspace", back_populates="labels")
    cards = relationship("Card", secondary="card_labels", back_populates="labels")

    def __repr__(self) -> str:
        """String representation of WorkspaceLabel."""
        return f"<WorkspaceLabel(id={self.id}, name={self.name}, color={self.color})>"

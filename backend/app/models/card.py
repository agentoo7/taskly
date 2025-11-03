"""Card model for tasks and features on boards."""

import enum
import uuid

from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class PriorityEnum(str, enum.Enum):
    """Priority levels for cards."""

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Card(Base):
    """Card model representing tasks/features on boards."""

    __tablename__ = "cards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    board_id = Column(
        UUID(as_uuid=True),
        ForeignKey("boards.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    column_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    card_metadata = Column(
        JSONB, default=dict, nullable=False
    )  # {"labels": [...], "acceptance_criteria": "..."}
    priority = Column(Enum(PriorityEnum), default=PriorityEnum.NONE, nullable=False)
    story_points = Column(Integer, nullable=True)
    due_date = Column(Date, nullable=True)
    position = Column(Integer, nullable=False, default=0)
    sprint_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sprints.id", ondelete="SET NULL"),
        nullable=True,
    )
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
    board = relationship("Board", back_populates="cards")
    creator = relationship("User", back_populates="created_cards", foreign_keys=[created_by])
    assignees = relationship(
        "User",
        secondary="card_assignees",
        back_populates="assigned_cards",
        viewonly=True,
    )
    labels = relationship(
        "WorkspaceLabel",
        secondary="card_labels",
        back_populates="cards",
        viewonly=True,
    )
    sprint = relationship("Sprint", back_populates="cards")
    activities = relationship(
        "CardActivity",
        back_populates="card",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # Indexes
    __table_args__ = (
        Index("ix_cards_board_position", "board_id", "position"),
        Index("ix_cards_card_metadata_gin", "card_metadata", postgresql_using="gin"),
    )

    def __repr__(self) -> str:
        """String representation of Card."""
        return f"<Card(id={self.id}, title={self.title})>"

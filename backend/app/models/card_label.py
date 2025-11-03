"""CardLabel join table for card labels."""

from sqlalchemy import Column, DateTime, ForeignKey, PrimaryKeyConstraint, func
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class CardLabel(Base):
    """Join table for card labels."""

    __tablename__ = "card_labels"

    card_id = Column(
        UUID(as_uuid=True),
        ForeignKey("cards.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    label_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workspace_labels.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    assigned_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Composite primary key
    __table_args__ = (PrimaryKeyConstraint("card_id", "label_id"),)

    def __repr__(self) -> str:
        """String representation of CardLabel."""
        return f"<CardLabel(card_id={self.card_id}, label_id={self.label_id})>"

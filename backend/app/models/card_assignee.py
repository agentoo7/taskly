"""CardAssignee join table for card assignments."""

from sqlalchemy import Column, DateTime, ForeignKey, PrimaryKeyConstraint, func
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class CardAssignee(Base):
    """Join table for card assignments."""

    __tablename__ = "card_assignees"

    card_id = Column(
        UUID(as_uuid=True),
        ForeignKey("cards.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    assigned_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Composite primary key
    __table_args__ = (PrimaryKeyConstraint("card_id", "user_id"),)

    def __repr__(self) -> str:
        """String representation of CardAssignee."""
        return f"<CardAssignee(card_id={self.card_id}, user_id={self.user_id})>"

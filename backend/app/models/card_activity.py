"""Card activity model for tracking card history and changes."""

import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class CardActivity(Base):
    """Card activity model representing card change history."""

    __tablename__ = "card_activities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    card_id = Column(
        UUID(as_uuid=True),
        ForeignKey("cards.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    action = Column(String(50), nullable=False)  # "created", "moved", "updated", etc.
    activity_metadata = Column(
        JSONB, default=dict, nullable=False
    )  # Additional activity data
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    card = relationship("Card", back_populates="activities")
    user = relationship("User", back_populates="card_activities")

    def __repr__(self) -> str:
        """String representation of CardActivity."""
        return f"<CardActivity(id={self.id}, card_id={self.card_id}, action={self.action})>"

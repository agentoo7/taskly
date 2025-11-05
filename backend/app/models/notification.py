"""Notification model for user notifications."""

import enum
import uuid

from sqlalchemy import Column, DateTime, Enum as SQLEnum, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class NotificationType(str, enum.Enum):
    """Notification types."""

    COMMENT_MENTION = "comment_mention"
    CARD_ASSIGNED = "card_assigned"
    CARD_DUE_SOON = "card_due_soon"


class Notification(Base):
    """Notification model for user notifications."""

    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    type = Column(SQLEnum(NotificationType), nullable=False)
    card_id = Column(
        UUID(as_uuid=True),
        ForeignKey("cards.id", ondelete="CASCADE"),
        nullable=True,
    )
    comment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("card_comments.id", ondelete="CASCADE"),
        nullable=True,
    )
    title = Column(String(255), nullable=False)
    message = Column(String(500), nullable=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="notifications")
    card = relationship("Card")
    comment = relationship("CardComment")

    def __repr__(self) -> str:
        """String representation of Notification."""
        return f"<Notification(id={self.id}, user_id={self.user_id}, type={self.type})>"

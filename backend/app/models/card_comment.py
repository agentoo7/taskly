"""Card comment model for comments on cards."""

import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class CardComment(Base):
    """Card comment model representing user comments on cards."""

    __tablename__ = "card_comments"

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
    text = Column(Text, nullable=False)  # Markdown supported
    comment_metadata = Column(
        JSONB, default=dict, nullable=False
    )  # Store mentioned_users: [user_id, ...]
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete

    # Relationships
    card = relationship("Card", back_populates="comments")
    author = relationship("User", back_populates="card_comments")

    def __repr__(self) -> str:
        """String representation of CardComment."""
        return f"<CardComment(id={self.id}, card_id={self.card_id})>"

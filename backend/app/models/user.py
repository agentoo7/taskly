"""User model for authentication and user management."""

import uuid

from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    """User model representing authenticated users from GitHub OAuth."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    github_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    avatar_url = Column(String(500), nullable=True)
    github_access_token = Column(String(500), nullable=True)  # TODO: Encrypt in production
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    created_workspaces = relationship(
        "Workspace",
        back_populates="creator",
        foreign_keys="Workspace.created_by",
    )
    workspaces = relationship(
        "Workspace",
        secondary="workspace_members",
        back_populates="members",
        viewonly=True,
    )
    created_cards = relationship(
        "Card",
        back_populates="creator",
        foreign_keys="Card.created_by",
    )
    assigned_cards = relationship(
        "Card",
        secondary="card_assignees",
        back_populates="assignees",
        viewonly=True,
    )
    card_activities = relationship(
        "CardActivity",
        back_populates="user",
    )

    def __repr__(self) -> str:
        """String representation of User."""
        return f"<User(id={self.id}, username={self.username})>"

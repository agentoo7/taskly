"""GitRepository model for GitHub repository cache."""

import uuid

from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class GitRepository(Base):
    """GitRepository model for caching GitHub repository data."""

    __tablename__ = "git_repositories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    github_id = Column(Integer, unique=True, nullable=False, index=True)
    owner = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    full_name = Column(String(500), nullable=False)
    url = Column(String(500), nullable=False)
    default_branch = Column(String(100), default="main", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    pull_requests = relationship(
        "PullRequest", back_populates="repository", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation of GitRepository."""
        return f"<GitRepository(id={self.id}, full_name={self.full_name})>"

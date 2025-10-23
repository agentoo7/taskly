"""PullRequest model for caching PR data from GitHub."""

import enum
import uuid

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class PRStatusEnum(str, enum.Enum):
    """Status levels for pull requests."""

    OPEN = "open"
    CLOSED = "closed"
    MERGED = "merged"


class PullRequest(Base):
    """PullRequest model for caching GitHub PR data."""

    __tablename__ = "pull_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    github_id = Column(Integer, unique=True, nullable=False, index=True)
    repository_id = Column(
        UUID(as_uuid=True),
        ForeignKey("git_repositories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    pr_number = Column(Integer, nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    author = Column(String(255), nullable=False)
    status = Column(Enum(PRStatusEnum), default=PRStatusEnum.OPEN, nullable=False)
    url = Column(String(500), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    repository = relationship("GitRepository", back_populates="pull_requests")

    def __repr__(self) -> str:
        """String representation of PullRequest."""
        return f"<PullRequest(id={self.id}, pr_number={self.pr_number}, status={self.status})>"

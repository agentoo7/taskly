"""Sprint model for time-boxed iterations."""

import enum
import uuid

from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class SprintStatusEnum(str, enum.Enum):
    """Status levels for sprints."""

    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Sprint(Base):
    """Sprint model representing time-boxed iterations."""

    __tablename__ = "sprints"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    board_id = Column(
        UUID(as_uuid=True),
        ForeignKey("boards.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(100), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    goal = Column(Text, nullable=True)
    capacity_points = Column(Integer, nullable=True)
    status = Column(Enum(SprintStatusEnum), default=SprintStatusEnum.PLANNED, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    board = relationship("Board")
    cards = relationship("Card", back_populates="sprint")

    def __repr__(self) -> str:
        """String representation of Sprint."""
        return f"<Sprint(id={self.id}, name={self.name}, status={self.status})>"

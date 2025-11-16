"""Card activity model for tracking card history and changes."""

import enum
import uuid

from sqlalchemy import Column, DateTime, Enum as SQLEnum, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class ActivityAction(str, enum.Enum):
    """Activity action types for card changes."""

    CREATED = "created"
    TITLE_CHANGED = "title_changed"
    DESCRIPTION_UPDATED = "description_updated"
    MOVED = "moved"
    ASSIGNED = "assigned"
    UNASSIGNED = "unassigned"
    LABEL_ADDED = "label_added"
    LABEL_REMOVED = "label_removed"
    DUE_DATE_SET = "due_date_set"
    DUE_DATE_CLEARED = "due_date_cleared"
    PRIORITY_CHANGED = "priority_changed"
    COMMENTED = "commented"


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
    action = Column(SQLEnum(ActivityAction, values_callable=lambda obj: [e.value for e in obj]), nullable=False)
    activity_metadata = Column(
        JSONB, default=dict, nullable=False
    )  # Context: from_value, to_value, column_names, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    card = relationship("Card", back_populates="activities")
    user = relationship("User", back_populates="card_activities")

    def to_description(self) -> str:
        """Generate human-readable activity description."""
        if self.action == ActivityAction.MOVED:
            from_col = self.activity_metadata.get("from_column", "Unknown")
            to_col = self.activity_metadata.get("to_column", "Unknown")
            return f"moved from {from_col} to {to_col}"
        elif self.action == ActivityAction.ASSIGNED:
            assignee = self.activity_metadata.get("assignee_name", "someone")
            return f"assigned to {assignee}"
        elif self.action == ActivityAction.UNASSIGNED:
            assignee = self.activity_metadata.get("assignee_name", "someone")
            return f"unassigned {assignee}"
        elif self.action == ActivityAction.LABEL_ADDED:
            label = self.activity_metadata.get("label_name", "label")
            return f"added label {label}"
        elif self.action == ActivityAction.LABEL_REMOVED:
            label = self.activity_metadata.get("label_name", "label")
            return f"removed label {label}"
        elif self.action == ActivityAction.DUE_DATE_SET:
            date = self.activity_metadata.get("due_date", "")
            return f"set due date to {date}"
        elif self.action == ActivityAction.DUE_DATE_CLEARED:
            return "cleared due date"
        elif self.action == ActivityAction.PRIORITY_CHANGED:
            old_priority = self.activity_metadata.get("old_priority", "none")
            new_priority = self.activity_metadata.get("new_priority", "none")
            return f"changed priority from {old_priority} to {new_priority}"
        elif self.action == ActivityAction.TITLE_CHANGED:
            return "changed the title"
        elif self.action == ActivityAction.DESCRIPTION_UPDATED:
            return "updated the description"
        elif self.action == ActivityAction.CREATED:
            return "created this card"
        elif self.action == ActivityAction.COMMENTED:
            return "commented"
        else:
            return self.action.value.replace("_", " ")

    def __repr__(self) -> str:
        """String representation of CardActivity."""
        return f"<CardActivity(id={self.id}, card_id={self.card_id}, action={self.action})>"

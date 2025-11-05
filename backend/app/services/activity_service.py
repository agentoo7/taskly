"""Service layer for activity logging."""

from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.card_activity import ActivityAction, CardActivity
from app.repositories.activity_repository import ActivityRepository


class ActivityService:
    """Service for activity logging."""

    def __init__(self, db: AsyncSession):
        """Initialize service with database session."""
        self.db = db
        self.repo = ActivityRepository(db)

    async def log_activity(
        self,
        card_id: UUID,
        user_id: UUID,
        action: ActivityAction,
        metadata: Optional[dict] = None,
    ) -> CardActivity:
        """Log a card activity."""
        return await self.repo.create(
            card_id=card_id, user_id=user_id, action=action, activity_metadata=metadata or {}
        )

    # Helper methods for common activities

    async def log_card_created(self, card_id: UUID, user_id: UUID) -> CardActivity:
        """Log card creation activity."""
        return await self.log_activity(card_id, user_id, ActivityAction.CREATED)

    async def log_card_moved(
        self, card_id: UUID, user_id: UUID, from_column: str, to_column: str
    ) -> CardActivity:
        """Log card moved activity."""
        return await self.log_activity(
            card_id,
            user_id,
            ActivityAction.MOVED,
            {"from_column": from_column, "to_column": to_column},
        )

    async def log_user_assigned(
        self, card_id: UUID, user_id: UUID, assignee_name: str
    ) -> CardActivity:
        """Log user assignment activity."""
        return await self.log_activity(
            card_id, user_id, ActivityAction.ASSIGNED, {"assignee_name": assignee_name}
        )

    async def log_user_unassigned(
        self, card_id: UUID, user_id: UUID, assignee_name: str
    ) -> CardActivity:
        """Log user unassignment activity."""
        return await self.log_activity(
            card_id, user_id, ActivityAction.UNASSIGNED, {"assignee_name": assignee_name}
        )

    async def log_label_added(
        self, card_id: UUID, user_id: UUID, label_name: str
    ) -> CardActivity:
        """Log label added activity."""
        return await self.log_activity(
            card_id, user_id, ActivityAction.LABEL_ADDED, {"label_name": label_name}
        )

    async def log_label_removed(
        self, card_id: UUID, user_id: UUID, label_name: str
    ) -> CardActivity:
        """Log label removed activity."""
        return await self.log_activity(
            card_id, user_id, ActivityAction.LABEL_REMOVED, {"label_name": label_name}
        )

    async def log_due_date_set(
        self, card_id: UUID, user_id: UUID, due_date: str
    ) -> CardActivity:
        """Log due date set activity."""
        return await self.log_activity(
            card_id, user_id, ActivityAction.DUE_DATE_SET, {"due_date": due_date}
        )

    async def log_due_date_cleared(self, card_id: UUID, user_id: UUID) -> CardActivity:
        """Log due date cleared activity."""
        return await self.log_activity(card_id, user_id, ActivityAction.DUE_DATE_CLEARED)

    async def log_priority_changed(
        self, card_id: UUID, user_id: UUID, old_priority: str, new_priority: str
    ) -> CardActivity:
        """Log priority change activity."""
        return await self.log_activity(
            card_id,
            user_id,
            ActivityAction.PRIORITY_CHANGED,
            {"old_priority": old_priority, "new_priority": new_priority},
        )

    async def log_title_changed(self, card_id: UUID, user_id: UUID) -> CardActivity:
        """Log title change activity."""
        return await self.log_activity(card_id, user_id, ActivityAction.TITLE_CHANGED)

    async def log_description_updated(self, card_id: UUID, user_id: UUID) -> CardActivity:
        """Log description update activity."""
        return await self.log_activity(card_id, user_id, ActivityAction.DESCRIPTION_UPDATED)

    async def log_comment_created(self, card_id: UUID, user_id: UUID) -> CardActivity:
        """Log comment creation activity."""
        return await self.log_activity(card_id, user_id, ActivityAction.COMMENTED)

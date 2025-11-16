"""Repository for card activity database operations."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.card_activity import ActivityAction, CardActivity


class ActivityRepository:
    """Repository for card activity operations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository with database session."""
        self.db = db

    async def create(
        self,
        card_id: UUID,
        user_id: UUID,
        action: ActivityAction,
        activity_metadata: dict | None = None,
    ) -> CardActivity:
        """Create a new activity."""
        activity = CardActivity(
            card_id=card_id,
            user_id=user_id,
            action=action,
            activity_metadata=activity_metadata or {},
        )
        self.db.add(activity)
        await self.db.flush()
        await self.db.refresh(activity, ["user"])
        return activity

    async def get_by_card(
        self, card_id: UUID, offset: int = 0, limit: int = 20
    ) -> tuple[list[CardActivity], int]:
        """Get activities for a card with pagination."""
        # Get total count
        count_stmt = select(func.count(CardActivity.id)).where(CardActivity.card_id == card_id)
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar_one()

        # Get activities
        stmt = (
            select(CardActivity)
            .options(joinedload(CardActivity.user))
            .where(CardActivity.card_id == card_id)
            .order_by(CardActivity.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        activities = list(result.scalars().all())

        return activities, total

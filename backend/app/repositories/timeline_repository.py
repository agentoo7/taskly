"""Repository for card timeline (combined comments and activities)."""

from typing import Union
from uuid import UUID

from sqlalchemy import and_, func, select, union_all
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.card_activity import CardActivity
from app.models.card_comment import CardComment


class TimelineRepository:
    """Repository for card timeline operations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository with database session."""
        self.db = db

    async def get_timeline(
        self, card_id: UUID, offset: int = 0, limit: int = 20
    ) -> tuple[list[Union[CardComment, CardActivity]], int]:
        """Get combined timeline (comments + activities) for a card with pagination."""
        # Get total count of comments (excluding soft-deleted)
        comment_count_stmt = select(func.count(CardComment.id)).where(
            and_(CardComment.card_id == card_id, CardComment.deleted_at.is_(None))
        )
        comment_count_result = await self.db.execute(comment_count_stmt)
        comment_count = comment_count_result.scalar_one()

        # Get total count of activities
        activity_count_stmt = select(func.count(CardActivity.id)).where(
            CardActivity.card_id == card_id
        )
        activity_count_result = await self.db.execute(activity_count_stmt)
        activity_count = activity_count_result.scalar_one()

        total = comment_count + activity_count

        # Fetch comments
        comment_stmt = (
            select(CardComment)
            .options(joinedload(CardComment.author))
            .where(and_(CardComment.card_id == card_id, CardComment.deleted_at.is_(None)))
        )
        comment_result = await self.db.execute(comment_stmt)
        comments = list(comment_result.scalars().all())

        # Fetch activities
        activity_stmt = (
            select(CardActivity)
            .options(joinedload(CardActivity.user))
            .where(CardActivity.card_id == card_id)
        )
        activity_result = await self.db.execute(activity_stmt)
        activities = list(activity_result.scalars().all())

        # Combine and sort by created_at descending
        all_items: list[Union[CardComment, CardActivity]] = comments + activities  # type: ignore
        all_items.sort(key=lambda x: x.created_at, reverse=True)

        # Apply pagination
        paginated_items = all_items[offset : offset + limit]

        return paginated_items, total

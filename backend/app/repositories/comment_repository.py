"""Repository for card comment database operations."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.card_comment import CardComment


class CommentRepository:
    """Repository for card comment operations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository with database session."""
        self.db = db

    async def create(
        self, card_id: UUID, user_id: UUID, text: str, comment_metadata: Optional[dict] = None
    ) -> CardComment:
        """Create a new comment."""
        comment = CardComment(
            card_id=card_id,
            user_id=user_id,
            text=text,
            comment_metadata=comment_metadata or {},
        )
        self.db.add(comment)
        await self.db.flush()
        await self.db.refresh(comment, ["author"])
        return comment

    async def get_by_id(self, comment_id: UUID) -> Optional[CardComment]:
        """Get comment by ID."""
        stmt = (
            select(CardComment)
            .options(joinedload(CardComment.author))
            .where(and_(CardComment.id == comment_id, CardComment.deleted_at.is_(None)))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_card(
        self, card_id: UUID, offset: int = 0, limit: int = 20
    ) -> tuple[list[CardComment], int]:
        """Get comments for a card with pagination."""
        # Get total count
        count_stmt = select(func.count(CardComment.id)).where(
            and_(CardComment.card_id == card_id, CardComment.deleted_at.is_(None))
        )
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar_one()

        # Get comments
        stmt = (
            select(CardComment)
            .options(joinedload(CardComment.author))
            .where(and_(CardComment.card_id == card_id, CardComment.deleted_at.is_(None)))
            .order_by(CardComment.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        comments = list(result.scalars().all())

        return comments, total

    async def update(self, comment_id: UUID, text: str) -> Optional[CardComment]:
        """Update comment text."""
        comment = await self.get_by_id(comment_id)
        if not comment:
            return None

        comment.text = text
        await self.db.flush()
        await self.db.refresh(comment)
        return comment

    async def soft_delete(self, comment_id: UUID) -> bool:
        """Soft delete a comment."""
        comment = await self.get_by_id(comment_id)
        if not comment:
            return False

        comment.deleted_at = datetime.utcnow()
        await self.db.flush()
        return True

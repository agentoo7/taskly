"""Service layer for comment business logic."""

import re
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.card_comment import CardComment
from app.repositories.comment_repository import CommentRepository


class CommentService:
    """Service for comment operations."""

    def __init__(self, db: AsyncSession):
        """Initialize service with database session."""
        self.db = db
        self.repo = CommentRepository(db)

    def parse_mentions(self, text: str) -> list[str]:
        """Parse @mentions from comment text and return list of usernames."""
        # Match @username pattern (alphanumeric, underscore, hyphen)
        pattern = r"@([a-zA-Z0-9_-]+)"
        mentions = re.findall(pattern, text)
        return mentions

    async def create_comment(
        self, card_id: UUID, user_id: UUID, text: str
    ) -> tuple[CardComment, list[str]]:
        """
        Create a new comment.

        Returns tuple of (comment, mentioned_usernames).
        """
        # Parse mentions
        mentioned_usernames = self.parse_mentions(text)

        # Store mentioned usernames in metadata
        metadata = {"mentioned_usernames": mentioned_usernames} if mentioned_usernames else {}

        # Create comment
        comment = await self.repo.create(
            card_id=card_id, user_id=user_id, text=text, comment_metadata=metadata
        )

        return comment, mentioned_usernames

    async def update_comment(
        self, comment_id: UUID, text: str, user_id: UUID
    ) -> Optional[CardComment]:
        """Update comment text (with authorization check)."""
        # Authorization check handled at API layer
        comment = await self.repo.get_by_id(comment_id)
        if not comment or comment.user_id != user_id:
            return None

        # Parse mentions
        mentioned_usernames = self.parse_mentions(text)
        if mentioned_usernames:
            comment.comment_metadata = {"mentioned_usernames": mentioned_usernames}

        return await self.repo.update(comment_id, text)

    async def delete_comment(self, comment_id: UUID, user_id: UUID) -> bool:
        """Delete comment (with authorization check)."""
        # Authorization check handled at API layer
        comment = await self.repo.get_by_id(comment_id)
        if not comment or comment.user_id != user_id:
            return False

        return await self.repo.soft_delete(comment_id)

"""Assignee repository for database operations."""

from typing import Sequence
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.card_assignee import CardAssignee
from app.models.user import User


class AssigneeRepository:
    """Repository for assignee-related database operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize assignee repository."""
        self.session = session

    async def assign_user_to_card(self, card_id: UUID, user_id: UUID) -> CardAssignee:
        """Assign a user to a card."""
        assignee = CardAssignee(card_id=card_id, user_id=user_id)
        self.session.add(assignee)
        await self.session.flush()
        return assignee

    async def unassign_user_from_card(self, card_id: UUID, user_id: UUID) -> bool:
        """Unassign a user from a card."""
        result = await self.session.execute(
            delete(CardAssignee).where(
                CardAssignee.card_id == card_id, CardAssignee.user_id == user_id
            )
        )
        await self.session.flush()
        return result.rowcount > 0

    async def get_card_assignees(self, card_id: UUID) -> Sequence[User]:
        """Get all users assigned to a card."""
        result = await self.session.execute(
            select(User)
            .join(CardAssignee, CardAssignee.user_id == User.id)
            .where(CardAssignee.card_id == card_id)
        )
        return result.scalars().all()

    async def is_user_assigned(self, card_id: UUID, user_id: UUID) -> bool:
        """Check if a user is assigned to a card."""
        result = await self.session.execute(
            select(CardAssignee).where(
                CardAssignee.card_id == card_id, CardAssignee.user_id == user_id
            )
        )
        return result.scalar_one_or_none() is not None

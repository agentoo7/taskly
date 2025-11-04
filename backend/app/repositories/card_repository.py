"""Card repository for database operations."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.card import Card
from app.repositories.base import BaseRepository


class CardRepository(BaseRepository[Card]):
    """Repository for Card model operations."""

    def __init__(self, session: AsyncSession):
        """Initialize CardRepository.

        Args:
            session: Async database session
        """
        super().__init__(Card, session)

    async def get_by_board(self, board_id: UUID) -> list[Card]:
        """Get all cards on a board.

        Args:
            board_id: Board UUID

        Returns:
            List of Card instances ordered by position
        """
        result = await self.session.execute(
            select(Card).where(Card.board_id == board_id).order_by(Card.column_id, Card.position)
        )
        return list(result.scalars().all())

    async def get_by_column(self, board_id: UUID, column_id: UUID) -> list[Card]:
        """Get all cards in a specific column.

        Args:
            board_id: Board UUID
            column_id: Column UUID

        Returns:
            List of Card instances ordered by position
        """
        result = await self.session.execute(
            select(Card)
            .where(Card.board_id == board_id, Card.column_id == column_id)
            .order_by(Card.position)
        )
        return list(result.scalars().all())

    async def get_by_creator(self, user_id: UUID) -> list[Card]:
        """Get all cards created by a user.

        Args:
            user_id: User UUID

        Returns:
            List of Card instances
        """
        result = await self.session.execute(select(Card).where(Card.created_by == user_id))
        return list(result.scalars().all())

    async def get_with_board(self, card_id: UUID) -> Card | None:
        """Get card with board relationship loaded.

        Args:
            card_id: Card UUID

        Returns:
            Card instance with board loaded or None
        """
        result = await self.session.execute(
            select(Card).where(Card.id == card_id).options(selectinload(Card.board))
        )
        return result.scalar_one_or_none()

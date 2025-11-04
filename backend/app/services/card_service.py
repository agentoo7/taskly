"""Card service for managing cards and their metadata."""

import uuid
from datetime import datetime
from uuid import UUID

import structlog
from fastapi import HTTPException, status
from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.board import Board
from app.models.card import Card
from app.models.workspace_member import WorkspaceMember
from app.websockets.manager import manager

logger = structlog.get_logger(__name__)


class CardService:
    """Service for handling card operations."""

    def __init__(self, db: AsyncSession):
        """
        Initialize CardService.

        Args:
            db: Async database session
        """
        self.db = db

    async def create_card(
        self, board_id: UUID, column_id: UUID, title: str, user_id: UUID
    ) -> Card:
        """
        Create card at position 0, incrementing existing cards in column.

        Args:
            board_id: UUID of board
            column_id: UUID of column (must exist in board.columns)
            title: Card title (will be trimmed)
            user_id: UUID of user creating card

        Returns:
            Created card

        Raises:
            HTTPException: If user not workspace member or column invalid
        """
        logger.info(
            "card.create.start",
            board_id=str(board_id),
            column_id=str(column_id),
            title=title,
            user_id=str(user_id),
        )

        # Get board and verify permissions
        board = await self._get_board_with_permission(board_id, user_id)

        # Verify column exists in board
        column_exists = any(
            col.get("id") == str(column_id) for col in board.columns
        )
        if not column_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Column does not exist in board",
            )

        try:
            async with self.db.begin_nested():
                # Parse column_id to UUID if it's a string
                col_uuid = column_id if isinstance(column_id, UUID) else uuid.UUID(str(column_id))

                # Increment positions of existing cards in column
                await self.db.execute(
                    update(Card)
                    .where(
                        and_(
                            Card.board_id == board_id,
                            Card.column_id == col_uuid,
                        )
                    )
                    .values(position=Card.position + 1)
                )

                # Create new card at position 0
                card = Card(
                    board_id=board_id,
                    column_id=col_uuid,
                    title=title.strip(),
                    position=0,
                    created_by=user_id,
                )
                self.db.add(card)
                await self.db.flush()
                await self.db.refresh(card, ["assignees", "labels"])

            await self.db.commit()

            logger.info(
                "card.create.success",
                card_id=str(card.id),
                title=card.title,
                board_id=str(board_id),
                column_id=str(column_id),
            )

            # Broadcast card creation
            await manager.broadcast_to_board(
                board_id=board_id,
                message={
                    "event_type": "card_created",
                    "card_id": str(card.id),
                    "board_id": str(board_id),
                    "column_id": str(column_id),
                    "title": card.title,
                    "position": card.position,
                    "user_id": str(user_id),
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

            return card

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                "card.create.failed",
                error=str(e),
                error_type=type(e).__name__,
                board_id=str(board_id),
                user_id=str(user_id),
            )
            await self.db.rollback()
            raise

    async def get_board_cards(
        self, board_id: UUID, user_id: UUID, column_id: UUID | str | None = None
    ) -> list[Card]:
        """
        Fetch cards for board, optionally filtered by column.

        Args:
            board_id: UUID of board
            user_id: UUID of requesting user
            column_id: Optional UUID or string to filter by column

        Returns:
            List of cards ordered by position ascending
        """
        # Verify permissions
        await self._get_board_with_permission(board_id, user_id)

        query = (
            select(Card)
            .where(Card.board_id == board_id)
            .options(selectinload(Card.assignees), selectinload(Card.labels))
        )
        if column_id:
            col_uuid = column_id if isinstance(column_id, UUID) else uuid.UUID(str(column_id))
            query = query.where(Card.column_id == col_uuid)
        query = query.order_by(Card.position.asc())

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_card_by_id(self, card_id: UUID, user_id: UUID) -> Card:
        """
        Get card by ID with permission check.

        Args:
            card_id: UUID of card
            user_id: UUID of requesting user

        Returns:
            Card instance

        Raises:
            HTTPException: If card not found or user not workspace member
        """
        result = await self.db.execute(select(Card).where(Card.id == card_id))
        card = result.scalar_one_or_none()

        if not card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Card not found"
            )

        # Verify user has access via board's workspace
        await self._get_board_with_permission(card.board_id, user_id)

        return card

    async def update_card(
        self, card_id: UUID, user_id: UUID, updates: dict
    ) -> Card:
        """
        Update card fields.

        Args:
            card_id: UUID of card to update
            user_id: UUID of user updating card
            updates: Dictionary of fields to update

        Returns:
            Updated card

        Raises:
            HTTPException: If card not found or user not workspace member
        """
        # Get card with eagerly loaded relationships
        result = await self.db.execute(
            select(Card)
            .where(Card.id == card_id)
            .options(selectinload(Card.assignees), selectinload(Card.labels))
        )
        card = result.scalar_one_or_none()

        if not card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Card not found"
            )

        # Verify user has access via board's workspace
        await self._get_board_with_permission(card.board_id, user_id)

        logger.info(
            "card.update.start",
            card_id=str(card_id),
            updates=updates,
            user_id=str(user_id),
        )

        try:
            # Filter allowed fields
            allowed_fields = {
                "title",
                "description",
                "priority",
                "due_date",
                "story_points",
            }
            filtered_updates = {
                k: v for k, v in updates.items() if k in allowed_fields
            }

            # Apply updates
            for key, value in filtered_updates.items():
                if key == "title" and value:
                    value = value.strip()
                setattr(card, key, value)

            await self.db.commit()
            # Refresh to get updated timestamps, relationships already loaded
            await self.db.refresh(card)

            logger.info(
                "card.update.success",
                card_id=str(card_id),
                updated_fields=list(filtered_updates.keys()),
            )

            # Broadcast card update
            await manager.broadcast_to_board(
                board_id=card.board_id,
                message={
                    "event_type": "card_updated",
                    "card_id": str(card_id),
                    "board_id": str(card.board_id),
                    "column_id": str(card.column_id),
                    "updates": filtered_updates,
                    "user_id": str(user_id),
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

            return card

        except Exception as e:
            logger.error(
                "card.update.failed",
                error=str(e),
                error_type=type(e).__name__,
                card_id=str(card_id),
            )
            await self.db.rollback()
            raise

    async def delete_card(self, card_id: UUID, user_id: UUID) -> None:
        """
        Delete card and reorder remaining cards in column.

        Args:
            card_id: UUID of card to delete
            user_id: UUID of user deleting card

        Raises:
            HTTPException: If card not found or user not workspace member
        """
        card = await self.get_card_by_id(card_id, user_id)

        logger.info(
            "card.delete.start",
            card_id=str(card_id),
            title=card.title,
            user_id=str(user_id),
        )

        try:
            async with self.db.begin_nested():
                board_id = card.board_id
                column_id = card.column_id
                position = card.position

                # Delete card
                await self.db.delete(card)

                # Reorder remaining cards (decrement positions > deleted position)
                await self.db.execute(
                    update(Card)
                    .where(
                        and_(
                            Card.board_id == board_id,
                            Card.column_id == column_id,
                            Card.position > position,
                        )
                    )
                    .values(position=Card.position - 1)
                )

            await self.db.commit()

            logger.info(
                "card.delete.success",
                card_id=str(card_id),
                user_id=str(user_id),
            )

            # Broadcast card deletion
            await manager.broadcast_to_board(
                board_id=board_id,
                message={
                    "event_type": "card_deleted",
                    "card_id": str(card_id),
                    "board_id": str(board_id),
                    "column_id": str(column_id),
                    "user_id": str(user_id),
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

        except Exception as e:
            logger.error(
                "card.delete.failed",
                error=str(e),
                error_type=type(e).__name__,
                card_id=str(card_id),
            )
            await self.db.rollback()
            raise

    async def _get_board_with_permission(
        self, board_id: UUID, user_id: UUID
    ) -> Board:
        """
        Get board and verify user is workspace member.

        Args:
            board_id: UUID of board
            user_id: UUID of user

        Returns:
            Board instance

        Raises:
            HTTPException: If board not found or user not workspace member
        """
        result = await self.db.execute(select(Board).where(Board.id == board_id))
        board = result.scalar_one_or_none()

        if not board:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Board not found"
            )

        # Verify user is workspace member
        member_result = await self.db.execute(
            select(WorkspaceMember).where(
                and_(
                    WorkspaceMember.workspace_id == board.workspace_id,
                    WorkspaceMember.user_id == user_id,
                )
            )
        )

        if not member_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this workspace",
            )

        return board

"""Card movement service for handling card drag-and-drop and position management."""

from datetime import datetime
from uuid import UUID

import structlog
from fastapi import HTTPException, status
from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.board import Board
from app.models.card import Card
from app.models.card_activity import CardActivity
from app.models.workspace_member import WorkspaceMember
from app.websockets.manager import manager

logger = structlog.get_logger(__name__)


class CardMovementService:
    """Service for handling card movement and position recalculation."""

    def __init__(self, db: AsyncSession):
        """
        Initialize CardMovementService.

        Args:
            db: Async database session
        """
        self.db = db

    async def move_card(
        self,
        card_id: UUID,
        target_column_id: UUID,
        target_position: int,
        moved_by: UUID,
    ) -> Card:
        """
        Move card to new column/position with atomic position recalculation.

        Args:
            card_id: UUID of card to move
            target_column_id: Target column UUID
            target_position: Target position in column (0-indexed)
            moved_by: UUID of user moving card

        Returns:
            Updated card

        Raises:
            HTTPException: If card not found, user not authorized, or board archived
        """
        logger.info(
            "card.move.start",
            card_id=str(card_id),
            target_column_id=str(target_column_id),
            target_position=target_position,
            moved_by=str(moved_by),
        )

        # Get card and verify it exists
        result = await self.db.execute(select(Card).where(Card.id == card_id))
        card = result.scalar_one_or_none()

        if not card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Card not found"
            )

        # Get board and verify permissions
        board = await self._get_board_with_permission(card.board_id, moved_by)

        # Check if board is archived
        if board.archived:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot move cards in archived boards",
            )

        # Verify target column exists in board
        column_exists = any(
            col.get("id") == str(target_column_id) for col in board.columns
        )
        if not column_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Target column does not exist in board",
            )

        try:
            async with self.db.begin_nested():
                old_column_id = card.column_id
                old_position = card.position
                board_id = card.board_id

                # Get column name for activity logging
                old_column_name = next(
                    (col["name"] for col in board.columns if col.get("id") == str(old_column_id)),
                    "Unknown"
                )
                new_column_name = next(
                    (col["name"] for col in board.columns if col.get("id") == str(target_column_id)),
                    "Unknown"
                )

                if old_column_id == target_column_id:
                    # Same column: reorder
                    await self._reorder_within_column(
                        board_id, old_column_id, old_position, target_position
                    )
                else:
                    # Different column: remove from old, insert in new
                    await self._remove_from_column(board_id, old_column_id, old_position)
                    await self._insert_into_column(
                        board_id, target_column_id, target_position
                    )

                # Update card
                card.column_id = target_column_id
                card.position = target_position
                await self.db.flush()

                # Log activity
                activity = CardActivity(
                    card_id=card_id,
                    user_id=moved_by,
                    action="moved",
                    activity_metadata={
                        "from_column": str(old_column_id),
                        "from_column_name": old_column_name,
                        "to_column": str(target_column_id),
                        "to_column_name": new_column_name,
                        "from_position": old_position,
                        "to_position": target_position,
                    },
                )
                self.db.add(activity)

                await self.db.flush()
                await self.db.refresh(card)

            await self.db.commit()

            logger.info(
                "card.move.success",
                card_id=str(card_id),
                old_column_id=str(old_column_id),
                new_column_id=str(target_column_id),
                old_position=old_position,
                new_position=target_position,
            )

            # Broadcast card movement via WebSocket
            await manager.broadcast_to_board(
                board_id=str(board_id),
                message={
                    "event_type": "card_moved",
                    "card_id": str(card_id),
                    "board_id": str(board_id),
                    "old_column_id": str(old_column_id),
                    "new_column_id": str(target_column_id),
                    "old_column_name": old_column_name,
                    "new_column_name": new_column_name,
                    "old_position": old_position,
                    "new_position": target_position,
                    "moved_by": str(moved_by),
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

            return card

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                "card.move.failed",
                error=str(e),
                error_type=type(e).__name__,
                card_id=str(card_id),
            )
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to move card",
            ) from e

    async def bulk_move_cards(
        self,
        card_ids: list[UUID],
        target_column_id: UUID,
        target_position: int,
        moved_by: UUID,
    ) -> list[Card]:
        """
        Move multiple cards to new column/position as a group.

        Args:
            card_ids: List of card UUIDs to move
            target_column_id: Target column UUID
            target_position: Starting position in target column
            moved_by: UUID of user moving cards

        Returns:
            List of updated cards

        Raises:
            HTTPException: If cards not found, user not authorized, or board archived
        """
        logger.info(
            "card.bulk_move.start",
            card_ids=[str(cid) for cid in card_ids],
            target_column_id=str(target_column_id),
            target_position=target_position,
            moved_by=str(moved_by),
        )

        if not card_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No cards provided for bulk move",
            )

        moved_cards = []
        current_position = target_position

        try:
            for card_id in card_ids:
                card = await self.move_card(
                    card_id=card_id,
                    target_column_id=target_column_id,
                    target_position=current_position,
                    moved_by=moved_by,
                )
                moved_cards.append(card)
                current_position += 1

            logger.info(
                "card.bulk_move.success",
                card_count=len(moved_cards),
                target_column_id=str(target_column_id),
            )

            return moved_cards

        except Exception as e:
            logger.error(
                "card.bulk_move.failed",
                error=str(e),
                error_type=type(e).__name__,
                card_ids=[str(cid) for cid in card_ids],
            )
            raise

    async def _reorder_within_column(
        self,
        board_id: UUID,
        column_id: UUID,
        old_position: int,
        new_position: int,
    ) -> None:
        """
        Reorder cards within same column.

        Args:
            board_id: UUID of board
            column_id: UUID of column
            old_position: Current card position
            new_position: Target card position
        """
        if old_position == new_position:
            return

        if old_position < new_position:
            # Moving down: shift cards between old and new position up
            await self.db.execute(
                update(Card)
                .where(
                    and_(
                        Card.board_id == board_id,
                        Card.column_id == column_id,
                        Card.position > old_position,
                        Card.position <= new_position,
                    )
                )
                .values(position=Card.position - 1)
            )
        else:
            # Moving up: shift cards between new and old position down
            await self.db.execute(
                update(Card)
                .where(
                    and_(
                        Card.board_id == board_id,
                        Card.column_id == column_id,
                        Card.position >= new_position,
                        Card.position < old_position,
                    )
                )
                .values(position=Card.position + 1)
            )

    async def _remove_from_column(
        self, board_id: UUID, column_id: UUID, position: int
    ) -> None:
        """
        Remove card from column by shifting cards below up.

        Args:
            board_id: UUID of board
            column_id: UUID of column
            position: Position of card being removed
        """
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

    async def _insert_into_column(
        self, board_id: UUID, column_id: UUID, position: int
    ) -> None:
        """
        Insert card into column by shifting cards at/below position down.

        Args:
            board_id: UUID of board
            column_id: UUID of column
            position: Position to insert card at
        """
        await self.db.execute(
            update(Card)
            .where(
                and_(
                    Card.board_id == board_id,
                    Card.column_id == column_id,
                    Card.position >= position,
                )
            )
            .values(position=Card.position + 1)
        )

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

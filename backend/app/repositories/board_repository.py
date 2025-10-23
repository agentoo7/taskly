"""Board repository for database operations."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.board import Board
from app.repositories.base import BaseRepository


class BoardRepository(BaseRepository[Board]):
    """Repository for Board model operations."""

    def __init__(self, session: AsyncSession):
        """Initialize BoardRepository.

        Args:
            session: Async database session
        """
        super().__init__(Board, session)

    async def get_by_workspace(self, workspace_id: UUID) -> list[Board]:
        """Get all boards in a workspace.

        Args:
            workspace_id: Workspace UUID

        Returns:
            List of Board instances
        """
        result = await self.session.execute(select(Board).where(Board.workspace_id == workspace_id))
        return list(result.scalars().all())

    async def get_active_by_workspace(self, workspace_id: UUID) -> list[Board]:
        """Get all non-archived boards in a workspace.

        Args:
            workspace_id: Workspace UUID

        Returns:
            List of active Board instances
        """
        result = await self.session.execute(
            select(Board).where(
                Board.workspace_id == workspace_id,
                Board.archived == False,  # noqa: E712
            )
        )
        return list(result.scalars().all())

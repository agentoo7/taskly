"""Workspace repository for database operations."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workspace import Workspace
from app.repositories.base import BaseRepository


class WorkspaceRepository(BaseRepository[Workspace]):
    """Repository for Workspace model operations."""

    def __init__(self, session: AsyncSession):
        """Initialize WorkspaceRepository.

        Args:
            session: Async database session
        """
        super().__init__(Workspace, session)

    async def get_by_creator(self, user_id: UUID) -> list[Workspace]:
        """Get all workspaces created by a user.

        Args:
            user_id: User UUID

        Returns:
            List of Workspace instances
        """
        result = await self.session.execute(
            select(Workspace).where(Workspace.created_by == user_id)
        )
        return list(result.scalars().all())

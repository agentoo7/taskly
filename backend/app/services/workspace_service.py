"""Workspace service for managing workspaces and membership."""

from uuid import UUID

import structlog
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workspace import Workspace
from app.models.workspace_member import RoleEnum, WorkspaceMember
from app.websockets.manager import manager

logger = structlog.get_logger(__name__)


class WorkspaceService:
    """Service for handling workspace operations."""

    def __init__(self, db: AsyncSession):
        """
        Initialize WorkspaceService.

        Args:
            db: Async database session
        """
        self.db = db

    async def create_workspace(self, name: str, creator_id: UUID) -> Workspace:
        """
        Create workspace and add creator as admin.

        Args:
            name: Workspace name (will be trimmed)
            creator_id: UUID of user creating the workspace

        Returns:
            Created workspace with relationships loaded

        Raises:
            HTTPException: If database operation fails
        """
        logger.info(
            "workspace.create.start",
            workspace_name=name,
            creator_id=str(creator_id),
        )

        try:
            async with self.db.begin_nested():
                # Create workspace
                workspace = Workspace(name=name.strip(), created_by=creator_id)
                self.db.add(workspace)
                await self.db.flush()

                # Add creator as admin
                membership = WorkspaceMember(
                    user_id=creator_id, workspace_id=workspace.id, role=RoleEnum.ADMIN
                )
                self.db.add(membership)
                await self.db.flush()
                await self.db.refresh(workspace)

            logger.info(
                "workspace.create.success",
                workspace_id=str(workspace.id),
                workspace_name=workspace.name,
                creator_id=str(creator_id),
            )
            return workspace

        except Exception as e:
            logger.error(
                "workspace.create.failed",
                error=str(e),
                error_type=type(e).__name__,
                workspace_name=name,
                creator_id=str(creator_id),
            )
            raise

    async def get_user_workspaces(self, user_id: UUID) -> list[Workspace]:
        """
        Get all workspaces user is member of.

        Args:
            user_id: UUID of user to get workspaces for

        Returns:
            List of workspaces ordered by most recently updated
        """
        result = await self.db.execute(
            select(Workspace)
            .join(WorkspaceMember)
            .where(WorkspaceMember.user_id == user_id)
            .order_by(Workspace.updated_at.desc())
        )
        return list(result.scalars().all())

    async def get_workspace_by_id(self, workspace_id: UUID) -> Workspace | None:
        """
        Get workspace by ID.

        Args:
            workspace_id: UUID of workspace to retrieve

        Returns:
            Workspace if found, None otherwise
        """
        result = await self.db.execute(select(Workspace).where(Workspace.id == workspace_id))
        return result.scalar_one_or_none()

    async def update_workspace(
        self, workspace_id: UUID, updates: dict[str, str], user_id: UUID
    ) -> Workspace:
        """
        Update workspace (admin only).

        Args:
            workspace_id: UUID of workspace to update
            updates: Dictionary of fields to update
            user_id: UUID of user performing the update

        Returns:
            Updated workspace

        Raises:
            HTTPException: If workspace not found or user lacks permission
        """
        logger.info(
            "workspace.update.start",
            workspace_id=str(workspace_id),
            user_id=str(user_id),
            updates=updates,
        )

        try:
            # Check admin permission
            await self._check_admin(workspace_id, user_id)

            result = await self.db.execute(select(Workspace).where(Workspace.id == workspace_id))
            workspace = result.scalar_one_or_none()

            if not workspace:
                logger.warning(
                    "workspace.update.not_found",
                    workspace_id=str(workspace_id),
                )
                raise HTTPException(status_code=404, detail="Workspace not found")

            # Apply updates
            for key, value in updates.items():
                if hasattr(workspace, key):
                    setattr(workspace, key, value)

            await self.db.commit()
            await self.db.refresh(workspace)

            # Broadcast WebSocket event to workspace members
            await manager.broadcast_to_workspace(
                str(workspace_id),
                {
                    "event": "workspace_updated",
                    "data": {
                        "workspace_id": str(workspace.id),
                        "name": workspace.name,
                        "updated_by": str(user_id),
                    }
                },
                exclude_user_id=str(user_id)  # Don't send to user who made the change
            )

            logger.info(
                "workspace.update.success",
                workspace_id=str(workspace.id),
                workspace_name=workspace.name,
                user_id=str(user_id),
            )
            return workspace

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                "workspace.update.failed",
                error=str(e),
                error_type=type(e).__name__,
                workspace_id=str(workspace_id),
                user_id=str(user_id),
            )
            raise

    async def delete_workspace(self, workspace_id: UUID, user_id: UUID) -> None:
        """
        Delete workspace and all related data (admin only).

        Cascade delete will remove all boards, cards, and memberships.

        Args:
            workspace_id: UUID of workspace to delete
            user_id: UUID of user performing the deletion

        Raises:
            HTTPException: If workspace not found or user lacks permission
        """
        logger.info(
            "workspace.delete.start",
            workspace_id=str(workspace_id),
            user_id=str(user_id),
        )

        try:
            # Check admin permission
            await self._check_admin(workspace_id, user_id)

            result = await self.db.execute(select(Workspace).where(Workspace.id == workspace_id))
            workspace = result.scalar_one_or_none()

            if not workspace:
                logger.warning(
                    "workspace.delete.not_found",
                    workspace_id=str(workspace_id),
                )
                raise HTTPException(status_code=404, detail="Workspace not found")

            workspace_name = workspace.name

            # Broadcast WebSocket event before deletion
            await manager.broadcast_to_workspace(
                str(workspace_id),
                {
                    "event": "workspace_deleted",
                    "data": {
                        "workspace_id": str(workspace_id),
                        "deleted_by": str(user_id),
                    }
                }
            )

            await self.db.delete(workspace)
            await self.db.commit()

            logger.info(
                "workspace.delete.success",
                workspace_id=str(workspace_id),
                workspace_name=workspace_name,
                user_id=str(user_id),
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                "workspace.delete.failed",
                error=str(e),
                error_type=type(e).__name__,
                workspace_id=str(workspace_id),
                user_id=str(user_id),
            )
            raise

    async def check_workspace_member(self, workspace_id: UUID, user_id: UUID) -> bool:
        """
        Check if user is a member of workspace.

        Args:
            workspace_id: UUID of workspace to check
            user_id: UUID of user to check

        Returns:
            True if user is a member, False otherwise
        """
        result = await self.db.execute(
            select(WorkspaceMember).where(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id,
            )
        )
        return result.scalar_one_or_none() is not None

    async def _check_admin(self, workspace_id: UUID, user_id: UUID) -> None:
        """
        Check if user is admin of workspace.

        Args:
            workspace_id: UUID of workspace to check
            user_id: UUID of user to check

        Raises:
            HTTPException: If user is not an admin (403 Forbidden)
        """
        result = await self.db.execute(
            select(WorkspaceMember).where(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id,
                WorkspaceMember.role == RoleEnum.ADMIN,
            )
        )
        if not result.scalar_one_or_none():
            logger.warning(
                "workspace.permission_denied",
                workspace_id=str(workspace_id),
                user_id=str(user_id),
                required_role="admin",
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You must be a workspace admin to perform this action",
            )

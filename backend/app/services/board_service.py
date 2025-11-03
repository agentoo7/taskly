"""Board service for managing boards and columns."""

from datetime import datetime
from uuid import UUID, uuid4

import structlog
from fastapi import HTTPException, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.board import Board
from app.models.workspace_member import RoleEnum, WorkspaceMember
from app.websockets.manager import manager

logger = structlog.get_logger(__name__)

# Board templates with pre-populated columns
BOARD_TEMPLATES = {
    "blank": [],
    "kanban": [
        {"id": str(uuid4()), "name": "To Do", "position": 0},
        {"id": str(uuid4()), "name": "In Progress", "position": 1},
        {"id": str(uuid4()), "name": "In Review", "position": 2},
        {"id": str(uuid4()), "name": "Done", "position": 3},
    ],
}


class BoardService:
    """Service for handling board operations."""

    def __init__(self, db: AsyncSession):
        """
        Initialize BoardService.

        Args:
            db: Async database session
        """
        self.db = db

    async def create_board(
        self, workspace_id: UUID, name: str, user_id: UUID, template: str = "blank"
    ) -> Board:
        """
        Create board with optional template.

        Args:
            workspace_id: UUID of workspace to create board in
            name: Board name (will be trimmed)
            user_id: UUID of user creating the board
            template: Template name ("blank" or "kanban")

        Returns:
            Created board

        Raises:
            HTTPException: If user not workspace member or invalid template
        """
        logger.info(
            "board.create.start",
            workspace_id=str(workspace_id),
            board_name=name,
            user_id=str(user_id),
            template=template,
        )

        # Verify user is workspace member
        await self._check_workspace_member(workspace_id, user_id)

        # Validate and get template
        if template not in BOARD_TEMPLATES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid template: must be 'blank' or 'kanban'",
            )

        columns = BOARD_TEMPLATES[template].copy()

        try:
            board = Board(
                workspace_id=workspace_id, name=name.strip(), columns=columns
            )
            self.db.add(board)
            await self.db.commit()
            await self.db.refresh(board)

            logger.info(
                "board.create.success",
                board_id=str(board.id),
                board_name=board.name,
                workspace_id=str(workspace_id),
                user_id=str(user_id),
            )

            # Broadcast to workspace members
            await manager.broadcast_to_workspace(
                workspace_id=workspace_id,
                message={
                    "event_type": "board_created",
                    "board_id": str(board.id),
                    "board_name": board.name,
                    "user_id": str(user_id),
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

            return board

        except Exception as e:
            logger.error(
                "board.create.failed",
                error=str(e),
                error_type=type(e).__name__,
                workspace_id=str(workspace_id),
                user_id=str(user_id),
            )
            await self.db.rollback()
            raise

    async def get_workspace_boards(
        self, workspace_id: UUID, user_id: UUID, include_archived: bool = False
    ) -> list[Board]:
        """
        Get all boards in workspace.

        Args:
            workspace_id: UUID of workspace
            user_id: UUID of requesting user
            include_archived: Whether to include archived boards

        Returns:
            List of boards ordered by most recently updated
        """
        # Verify user is workspace member
        await self._check_workspace_member(workspace_id, user_id)

        query = select(Board).where(Board.workspace_id == workspace_id)

        if not include_archived:
            query = query.where(Board.archived == False)  # noqa: E712

        query = query.order_by(Board.updated_at.desc())

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_board_by_id(self, board_id: UUID, user_id: UUID) -> Board:
        """
        Get board by ID with permission check.

        Args:
            board_id: UUID of board
            user_id: UUID of requesting user

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
        await self._check_workspace_member(board.workspace_id, user_id)

        return board

    async def update_board(
        self,
        board_id: UUID,
        user_id: UUID,
        name: str | None = None,
        columns: list[dict] | None = None,
        archived: bool | None = None,
    ) -> Board:
        """
        Update board properties.

        Args:
            board_id: UUID of board to update
            user_id: UUID of user updating board
            name: Optional new board name
            columns: Optional new columns configuration
            archived: Optional archived status (admin only)

        Returns:
            Updated board

        Raises:
            HTTPException: If board not found, user not member, or validation fails
        """
        board = await self.get_board_by_id(board_id, user_id)

        # Check admin permission for archiving
        if archived is not None:
            await self._check_workspace_admin(board.workspace_id, user_id)

        action = None

        try:
            async with self.db.begin_nested():
                if name is not None:
                    old_name = board.name
                    board.name = name.strip()
                    action = "board_renamed"
                    logger.info(
                        "board.update.name",
                        board_id=str(board_id),
                        old_name=old_name,
                        new_name=board.name,
                    )

                if columns is not None:
                    # Validate columns structure
                    for i, col in enumerate(columns):
                        if "id" not in col or "name" not in col:
                            raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Invalid column structure: must have 'id' and 'name' fields",
                            )
                        col["position"] = i  # Ensure sequential positions

                    board.columns = columns
                    action = "column_updated"

                if archived is not None:
                    board.archived = archived
                    action = "board_archived" if archived else "board_unarchived"

                await self.db.flush()
                await self.db.refresh(board)

            logger.info(
                "board.update.success",
                board_id=str(board_id),
                user_id=str(user_id),
                action=action,
            )

            # Broadcast update
            if action:
                await manager.broadcast_to_board(
                    board_id=board_id,
                    message={
                        "event_type": "board_updated",
                        "board_id": str(board_id),
                        "user_id": str(user_id),
                        "action": action,
                        "data": {
                            "name": board.name,
                            "columns": board.columns,
                            "archived": board.archived,
                        },
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                )

            return board

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                "board.update.failed",
                error=str(e),
                error_type=type(e).__name__,
                board_id=str(board_id),
                user_id=str(user_id),
            )
            await self.db.rollback()
            raise

    async def delete_board(self, board_id: UUID, user_id: UUID) -> None:
        """
        Delete board (cascades to all cards).

        Args:
            board_id: UUID of board to delete
            user_id: UUID of user deleting board

        Raises:
            HTTPException: If board not found, user not admin, or deletion fails
        """
        board = await self.get_board_by_id(board_id, user_id)

        # Only admins can delete boards
        await self._check_workspace_admin(board.workspace_id, user_id)

        logger.info(
            "board.delete.start",
            board_id=str(board_id),
            board_name=board.name,
            user_id=str(user_id),
        )

        try:
            workspace_id = board.workspace_id
            await self.db.delete(board)
            await self.db.commit()

            logger.info(
                "board.delete.success",
                board_id=str(board_id),
                user_id=str(user_id),
            )

            # Broadcast deletion
            await manager.broadcast_to_workspace(
                workspace_id=workspace_id,
                message={
                    "event_type": "board_deleted",
                    "board_id": str(board_id),
                    "user_id": str(user_id),
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

        except Exception as e:
            logger.error(
                "board.delete.failed",
                error=str(e),
                error_type=type(e).__name__,
                board_id=str(board_id),
                user_id=str(user_id),
            )
            await self.db.rollback()
            raise

    async def _check_workspace_member(self, workspace_id: UUID, user_id: UUID) -> None:
        """
        Verify user is member of workspace.

        Args:
            workspace_id: UUID of workspace
            user_id: UUID of user

        Raises:
            HTTPException: If user not workspace member
        """
        result = await self.db.execute(
            select(WorkspaceMember).where(
                and_(
                    WorkspaceMember.workspace_id == workspace_id,
                    WorkspaceMember.user_id == user_id,
                )
            )
        )

        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this workspace",
            )

    async def _check_workspace_admin(self, workspace_id: UUID, user_id: UUID) -> None:
        """
        Verify user is admin of workspace.

        Args:
            workspace_id: UUID of workspace
            user_id: UUID of user

        Raises:
            HTTPException: If user not workspace admin
        """
        result = await self.db.execute(
            select(WorkspaceMember).where(
                and_(
                    WorkspaceMember.workspace_id == workspace_id,
                    WorkspaceMember.user_id == user_id,
                    WorkspaceMember.role == RoleEnum.ADMIN,
                )
            )
        )

        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Must be workspace admin",
            )

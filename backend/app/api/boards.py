"""Board API endpoints for managing boards and columns."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.board import (
    BoardCreate,
    BoardDetailResponse,
    BoardResponse,
    BoardUpdate,
)
from app.services.board_service import BoardService

router = APIRouter(prefix="/api", tags=["boards"])


@router.post(
    "/workspaces/{workspace_id}/boards",
    response_model=BoardResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_board(
    workspace_id: UUID,
    data: BoardCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BoardResponse:
    """
    Create new board in workspace.

    Args:
        workspace_id: UUID of workspace to create board in
        data: Board creation data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created board

    Raises:
        HTTPException: 401 if not authenticated, 403 if not workspace member,
                      400 if invalid template
    """
    service = BoardService(db)
    board = await service.create_board(
        workspace_id=workspace_id,
        name=data.name,
        user_id=current_user.id,
        template=data.template or "blank",
    )
    return BoardResponse.model_validate(board)


@router.get("/workspaces/{workspace_id}/boards", response_model=list[BoardResponse])
async def list_workspace_boards(
    workspace_id: UUID,
    include_archived: bool = Query(default=False),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[BoardResponse]:
    """
    List all boards in workspace.

    Args:
        workspace_id: UUID of workspace
        include_archived: Whether to include archived boards
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of boards ordered by most recently updated

    Raises:
        HTTPException: 401 if not authenticated, 403 if not workspace member
    """
    service = BoardService(db)
    boards = await service.get_workspace_boards(
        workspace_id=workspace_id,
        user_id=current_user.id,
        include_archived=include_archived,
    )
    return [BoardResponse.model_validate(b) for b in boards]


@router.get("/boards/{board_id}", response_model=BoardResponse)
async def get_board(
    board_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BoardResponse:
    """
    Get board details with columns.

    Args:
        board_id: UUID of board
        current_user: Current authenticated user
        db: Database session

    Returns:
        Board with columns

    Raises:
        HTTPException: 401 if not authenticated, 403 if not workspace member,
                      404 if board not found
    """
    service = BoardService(db)
    board = await service.get_board_by_id(board_id=board_id, user_id=current_user.id)
    return BoardResponse.model_validate(board)


@router.patch("/boards/{board_id}", response_model=BoardResponse)
async def update_board(
    board_id: UUID,
    data: BoardUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BoardResponse:
    """
    Update board properties (name, columns, archived status).

    Args:
        board_id: UUID of board to update
        data: Update data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated board

    Raises:
        HTTPException: 401 if not authenticated, 403 if not workspace member
                      (or not admin for archiving), 404 if board not found,
                      400 if invalid column structure
    """
    service = BoardService(db)
    board = await service.update_board(
        board_id=board_id,
        user_id=current_user.id,
        name=data.name,
        columns=[c.model_dump() for c in data.columns] if data.columns else None,
        archived=data.archived,
    )
    return BoardResponse.model_validate(board)


@router.delete("/boards/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_board(
    board_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Delete board and all its cards (cascade).

    Args:
        board_id: UUID of board to delete
        current_user: Current authenticated user
        db: Database session

    Raises:
        HTTPException: 401 if not authenticated, 403 if not workspace admin,
                      404 if board not found
    """
    service = BoardService(db)
    await service.delete_board(board_id=board_id, user_id=current_user.id)

"""Workspace API endpoints for managing workspaces."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import check_workspace_member, get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.workspace import (
    WorkspaceCreate,
    WorkspaceDetailResponse,
    WorkspaceResponse,
    WorkspaceUpdate,
)
from app.services.workspace_service import WorkspaceService

router = APIRouter(prefix="/api/workspaces", tags=["workspaces"])


@router.post("", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    data: WorkspaceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> WorkspaceResponse:
    """
    Create new workspace with current user as admin.

    Args:
        data: Workspace creation data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created workspace

    Raises:
        HTTPException: 401 if not authenticated
    """
    service = WorkspaceService(db)
    workspace = await service.create_workspace(data.name, current_user.id)
    return WorkspaceResponse.model_validate(workspace)


@router.get("", response_model=list[WorkspaceResponse])
async def list_workspaces(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[WorkspaceResponse]:
    """
    List all workspaces user is member of.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of workspaces ordered by most recently updated

    Raises:
        HTTPException: 401 if not authenticated
    """
    service = WorkspaceService(db)
    workspaces = await service.get_user_workspaces(current_user.id)
    return [WorkspaceResponse.model_validate(w) for w in workspaces]


@router.get("/{workspace_id}", response_model=WorkspaceDetailResponse)
async def get_workspace(
    workspace_id: UUID,
    current_user: User = Depends(get_current_user),
    _: None = Depends(check_workspace_member),
    db: AsyncSession = Depends(get_db),
) -> WorkspaceDetailResponse:
    """
    Get workspace details with boards and members.

    Args:
        workspace_id: UUID of workspace to retrieve
        current_user: Current authenticated user
        _: Permission check dependency
        db: Database session

    Returns:
        Workspace with details

    Raises:
        HTTPException: 401 if not authenticated, 403 if not a member, 404 if not found
    """
    service = WorkspaceService(db)
    workspace = await service.get_workspace_by_id(workspace_id)

    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # For now, return empty lists for boards and members
    # These will be populated in future stories
    response_data = WorkspaceResponse.model_validate(workspace).model_dump()
    response_data["boards"] = []
    response_data["members"] = []
    return WorkspaceDetailResponse(**response_data)


@router.patch("/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(
    workspace_id: UUID,
    data: WorkspaceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> WorkspaceResponse:
    """
    Update workspace name (admin only).

    Args:
        workspace_id: UUID of workspace to update
        data: Workspace update data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated workspace

    Raises:
        HTTPException: 401 if not authenticated, 403 if not admin, 404 if not found
    """
    service = WorkspaceService(db)
    workspace = await service.update_workspace(
        workspace_id, data.model_dump(exclude_unset=True), current_user.id
    )
    return WorkspaceResponse.model_validate(workspace)


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workspace(
    workspace_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Delete workspace and all boards/cards (admin only).

    Cascade delete will remove all boards, cards, and memberships.

    Args:
        workspace_id: UUID of workspace to delete
        current_user: Current authenticated user
        db: Database session

    Raises:
        HTTPException: 401 if not authenticated, 403 if not admin, 404 if not found
    """
    service = WorkspaceService(db)
    await service.delete_workspace(workspace_id, current_user.id)

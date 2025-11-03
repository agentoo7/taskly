"""Label API endpoints for managing workspace labels."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.label import LabelAssignRequest, LabelCreate, LabelResponse, LabelUpdate
from app.services.label_service import LabelService

router = APIRouter(prefix="/api", tags=["labels"])


@router.get("/workspaces/{workspace_id}/labels", response_model=list[LabelResponse])
async def list_workspace_labels(
    workspace_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[LabelResponse]:
    """
    List all labels for a workspace.

    Args:
        workspace_id: Workspace ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of workspace labels

    Raises:
        HTTPException: 403 if user is not a workspace member
    """
    service = LabelService(db)
    try:
        return await service.get_workspace_labels(workspace_id, current_user.id)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post(
    "/workspaces/{workspace_id}/labels",
    response_model=LabelResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_label(
    workspace_id: UUID,
    data: LabelCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LabelResponse:
    """
    Create a new label in a workspace.

    Args:
        workspace_id: Workspace ID
        data: Label creation data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created label

    Raises:
        HTTPException: 403 if user is not a workspace member
    """
    service = LabelService(db)
    try:
        label = await service.create_label(workspace_id, data, current_user.id)
        await db.commit()
        return label
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.patch("/labels/{label_id}", response_model=LabelResponse)
async def update_label(
    label_id: UUID,
    data: LabelUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LabelResponse:
    """
    Update a label's name and/or color.

    Args:
        label_id: Label ID
        data: Label update data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated label

    Raises:
        HTTPException: 404 if label not found, 403 if user is not a workspace member
    """
    service = LabelService(db)
    try:
        label = await service.update_label(label_id, data, current_user.id)
        await db.commit()
        return label
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete("/labels/{label_id}", status_code=status.HTTP_200_OK)
async def delete_label(
    label_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, int]:
    """
    Delete a label from workspace and remove from all cards.

    Args:
        label_id: Label ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Dictionary with count of affected cards

    Raises:
        HTTPException: 404 if label not found, 403 if user is not a workspace member
    """
    service = LabelService(db)
    try:
        return await service.delete_label(label_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post("/cards/{card_id}/labels", response_model=LabelResponse)
async def add_label_to_card(
    card_id: UUID,
    data: LabelAssignRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LabelResponse:
    """
    Add a label to a card.

    Args:
        card_id: Card ID
        data: Label assignment data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Added label

    Raises:
        HTTPException: 404 if label not found, 403 if user is not a workspace member
    """
    service = LabelService(db)
    try:
        label = await service.add_label_to_card(card_id, data.label_id, current_user.id)
        await db.commit()
        return label
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete("/cards/{card_id}/labels/{label_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_label_from_card(
    card_id: UUID,
    label_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Remove a label from a card.

    Args:
        card_id: Card ID
        label_id: Label ID
        current_user: Current authenticated user
        db: Database session

    Raises:
        HTTPException: 404 if label not found, 403 if user is not a workspace member
    """
    service = LabelService(db)
    try:
        success = await service.remove_label_from_card(card_id, label_id, current_user.id)
        if success:
            await db.commit()
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

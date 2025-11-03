"""Assignee API endpoints for managing card assignees."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.assignee import AssigneeRequest
from app.schemas.user import UserResponse
from app.services.assignee_service import AssigneeService

router = APIRouter(prefix="/api/cards", tags=["assignees"])


@router.post("/{card_id}/assignees", response_model=UserResponse)
async def assign_user_to_card(
    card_id: UUID,
    data: AssigneeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Assign a user to a card.

    Args:
        card_id: Card ID
        data: Assignee request data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Assigned user information

    Raises:
        HTTPException: 404 if card not found, 403 if user is not a workspace member,
                       400 if assignee is not a workspace member or already assigned
    """
    service = AssigneeService(db)
    try:
        user = await service.assign_user_to_card(card_id, data.user_id, current_user.id)
        await db.commit()
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete("/{card_id}/assignees/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unassign_user_from_card(
    card_id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Unassign a user from a card.

    Args:
        card_id: Card ID
        user_id: User ID to unassign
        current_user: Current authenticated user
        db: Database session

    Raises:
        HTTPException: 404 if card not found, 403 if user is not a workspace member
    """
    service = AssigneeService(db)
    try:
        success = await service.unassign_user_from_card(card_id, user_id, current_user.id)
        if success:
            await db.commit()
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

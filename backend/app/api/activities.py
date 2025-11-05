"""API endpoints for card activities."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.repositories.activity_repository import ActivityRepository
from app.schemas.activity import ActivityListResponse, ActivityResponse

router = APIRouter()


@router.get("/cards/{card_id}/activity", response_model=ActivityListResponse)
async def list_card_activities(
    card_id: UUID,
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of items to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ActivityListResponse:
    """List activities for a card with pagination."""
    repo = ActivityRepository(db)
    activities, total = await repo.get_by_card(card_id, offset=offset, limit=limit)

    return ActivityListResponse(
        items=[
            ActivityResponse(
                id=a.id,
                card_id=a.card_id,
                user=a.user,
                action=a.action,
                metadata=a.activity_metadata,
                description=a.to_description(),
                created_at=a.created_at,
            )
            for a in activities
        ],
        total=total,
        offset=offset,
        limit=limit,
    )

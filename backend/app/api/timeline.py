"""API endpoints for card timeline (combined comments and activities)."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.card_activity import CardActivity
from app.models.card_comment import CardComment
from app.models.user import User
from app.repositories.timeline_repository import TimelineRepository
from app.schemas.timeline import TimelineActivity, TimelineComment, TimelineItem, TimelineResponse

router = APIRouter()


@router.get("/cards/{card_id}/timeline", response_model=TimelineResponse)
async def get_card_timeline(
    card_id: UUID,
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of items to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TimelineResponse:
    """Get combined timeline (comments + activities) for a card with pagination."""
    repo = TimelineRepository(db)
    items, total = await repo.get_timeline(card_id, offset=offset, limit=limit)

    # Convert items to appropriate schemas
    timeline_items: list[TimelineItem] = []
    for item in items:
        if isinstance(item, CardComment):
            timeline_items.append(
                TimelineComment(
                    id=item.id,
                    card_id=item.card_id,
                    author=item.author,
                    text=item.text,
                    created_at=item.created_at,
                    updated_at=item.updated_at,
                )
            )
        elif isinstance(item, CardActivity):
            timeline_items.append(
                TimelineActivity(
                    id=item.id,
                    card_id=item.card_id,
                    user=item.user,
                    action=item.action,
                    description=item.to_description(),
                    created_at=item.created_at,
                )
            )

    return TimelineResponse(items=timeline_items, total=total, offset=offset, limit=limit)

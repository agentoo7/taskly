"""API endpoints for user notifications."""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import NotificationListResponse, NotificationResponse

router = APIRouter()


@router.get("/notifications", response_model=NotificationListResponse)
async def list_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NotificationListResponse:
    """List user notifications."""
    # Get notifications
    stmt = (
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(50)
    )
    result = await db.execute(stmt)
    notifications = list(result.scalars().all())

    # Get unread count
    unread_stmt = select(func.count(Notification.id)).where(
        Notification.user_id == current_user.id, Notification.read_at.is_(None)
    )
    unread_result = await db.execute(unread_stmt)
    unread_count = unread_result.scalar_one()

    return NotificationListResponse(
        items=[NotificationResponse.model_validate(n) for n in notifications],
        total=len(notifications),
        unread_count=unread_count,
    )


@router.patch("/notifications/{notification_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_notification_read(
    notification_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Mark a notification as read."""
    stmt = select(Notification).where(
        Notification.id == notification_id, Notification.user_id == current_user.id
    )
    result = await db.execute(stmt)
    notification = result.scalar_one_or_none()

    if notification and not notification.read_at:
        notification.read_at = datetime.now(timezone.utc)
        await db.commit()


@router.patch("/notifications/read-all", status_code=status.HTTP_204_NO_CONTENT)
async def mark_all_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Mark all notifications as read."""
    stmt = select(Notification).where(
        Notification.user_id == current_user.id, Notification.read_at.is_(None)
    )
    result = await db.execute(stmt)
    notifications = result.scalars().all()

    now = datetime.now(timezone.utc)
    for notification in notifications:
        notification.read_at = now

    await db.commit()

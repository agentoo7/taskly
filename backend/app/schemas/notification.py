"""Pydantic schemas for notifications."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.models.notification import NotificationType


class NotificationResponse(BaseModel):
    """Schema for notification response."""

    id: UUID
    user_id: UUID
    type: NotificationType
    card_id: Optional[UUID] = None
    comment_id: Optional[UUID] = None
    title: str
    message: str
    read_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class NotificationListResponse(BaseModel):
    """Schema for paginated notification list."""

    items: list[NotificationResponse]
    total: int
    unread_count: int

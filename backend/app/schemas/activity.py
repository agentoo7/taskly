"""Pydantic schemas for card activities."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.models.card_activity import ActivityAction


class ActivityUser(BaseModel):
    """Activity user information."""

    id: UUID
    username: str
    avatar_url: Optional[str] = None

    class Config:
        """Pydantic config."""

        from_attributes = True


class ActivityResponse(BaseModel):
    """Schema for activity response."""

    id: UUID
    card_id: UUID
    user: Optional[ActivityUser] = None
    action: ActivityAction
    metadata: dict
    description: str
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class ActivityListResponse(BaseModel):
    """Schema for paginated activity list."""

    items: list[ActivityResponse]
    total: int
    offset: int
    limit: int

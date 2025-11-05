"""Pydantic schemas for card timeline (combined comments and activities)."""

from datetime import datetime
from typing import Literal, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.card_activity import ActivityAction


class TimelineUser(BaseModel):
    """Timeline entry user information."""

    id: UUID
    username: str
    avatar_url: Optional[str] = None

    class Config:
        """Pydantic config."""

        from_attributes = True


class TimelineComment(BaseModel):
    """Timeline comment entry."""

    type: Literal["comment"] = "comment"
    id: UUID
    card_id: UUID
    author: Optional[TimelineUser] = None
    text: str
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class TimelineActivity(BaseModel):
    """Timeline activity entry."""

    type: Literal["activity"] = "activity"
    id: UUID
    card_id: UUID
    user: Optional[TimelineUser] = None
    action: ActivityAction
    description: str
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


TimelineItem = Union[TimelineComment, TimelineActivity]


class TimelineResponse(BaseModel):
    """Schema for paginated timeline."""

    items: list[TimelineItem] = Field(..., discriminator="type")
    total: int
    offset: int
    limit: int

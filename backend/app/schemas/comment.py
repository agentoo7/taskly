"""Pydantic schemas for card comments."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CommentAuthor(BaseModel):
    """Comment author information."""

    id: UUID
    username: str
    avatar_url: Optional[str] = None

    class Config:
        """Pydantic config."""

        from_attributes = True


class CommentCreate(BaseModel):
    """Schema for creating a new comment."""

    text: str = Field(..., min_length=1, description="Comment text (markdown supported)")


class CommentUpdate(BaseModel):
    """Schema for updating a comment."""

    text: str = Field(..., min_length=1, description="Updated comment text")


class CommentResponse(BaseModel):
    """Schema for comment response."""

    id: UUID
    card_id: UUID
    author: CommentAuthor
    text: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        """Pydantic config."""

        from_attributes = True


class CommentListResponse(BaseModel):
    """Schema for paginated comment list."""

    items: list[CommentResponse]
    total: int
    offset: int
    limit: int

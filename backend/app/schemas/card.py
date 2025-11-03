"""Card Pydantic schemas for request/response validation."""

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.card import PriorityEnum


class CardCreate(BaseModel):
    """Schema for creating a new card."""

    title: str = Field(..., min_length=1, max_length=255, description="Card title (max 255 chars)")
    column_id: UUID = Field(..., description="ID of the column this card belongs to")
    board_id: UUID = Field(..., description="ID of the board this card belongs to")

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        """Validate title is not empty or whitespace."""
        if not v or not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()


class CardUpdate(BaseModel):
    """Schema for updating card properties."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    priority: Optional[PriorityEnum] = None
    due_date: Optional[date] = None
    story_points: Optional[int] = Field(None, ge=0, le=99, description="Story points (0-99)")

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: Optional[str]) -> Optional[str]:
        """Validate title is not empty or whitespace if provided."""
        if v is not None and (not v or not v.strip()):
            raise ValueError("Title cannot be empty")
        return v.strip() if v else None

    @field_validator("story_points")
    @classmethod
    def validate_story_points(cls, v: Optional[int]) -> Optional[int]:
        """Validate story points are within range."""
        if v is not None and (v < 0 or v > 99):
            raise ValueError("Story points must be between 0 and 99")
        return v


class CardResponse(BaseModel):
    """Standard card response schema."""

    id: UUID
    board_id: UUID
    column_id: UUID
    title: str
    description: Optional[str] = None
    priority: PriorityEnum
    due_date: Optional[date] = None
    story_points: Optional[int] = None
    position: int
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # SQLAlchemy 2.0 compatibility


class CardDetailResponse(CardResponse):
    """Detailed card response with additional metadata for future expansion."""

    # Placeholders for future stories (comments, assignees, labels)
    # assignees: list[UUID] = []
    # labels: list[str] = []
    # comment_count: int = 0

    class Config:
        from_attributes = True

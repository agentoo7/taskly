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


class CardMoveRequest(BaseModel):
    """Schema for moving a card to a new column/position."""

    column_id: UUID = Field(..., description="Target column UUID")
    position: int = Field(..., ge=0, description="Target position in column (0-indexed)")

    @field_validator("position")
    @classmethod
    def validate_position(cls, v: int) -> int:
        """Validate position is non-negative."""
        if v < 0:
            raise ValueError("Position must be non-negative")
        return v


class BulkCardMoveRequest(BaseModel):
    """Schema for moving multiple cards to a new column/position."""

    card_ids: list[UUID] = Field(..., min_length=1, description="List of card UUIDs to move")
    column_id: UUID = Field(..., description="Target column UUID")
    position: int = Field(..., ge=0, description="Starting position in column (0-indexed)")

    @field_validator("card_ids")
    @classmethod
    def validate_card_ids(cls, v: list[UUID]) -> list[UUID]:
        """Validate card_ids is not empty."""
        if not v:
            raise ValueError("At least one card ID must be provided")
        return v

    @field_validator("position")
    @classmethod
    def validate_position(cls, v: int) -> int:
        """Validate position is non-negative."""
        if v < 0:
            raise ValueError("Position must be non-negative")
        return v

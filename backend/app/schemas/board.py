"""Board Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ColumnSchema(BaseModel):
    """Column definition within a board."""

    id: str  # UUID as string
    name: str
    position: int


class BoardCreate(BaseModel):
    """Schema for creating a new board."""

    name: str = Field(..., max_length=100, description="Board name (max 100 chars)")
    template: Optional[str] = Field(
        default="blank", description="Template: 'blank' or 'kanban'"
    )


class BoardUpdate(BaseModel):
    """Schema for updating board properties."""

    name: Optional[str] = Field(None, max_length=100)
    columns: Optional[list[ColumnSchema]] = None
    archived: Optional[bool] = None


class BoardResponse(BaseModel):
    """Standard board response schema."""

    id: UUID
    workspace_id: UUID
    name: str
    columns: list[ColumnSchema]
    archived: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # SQLAlchemy 2.0 compatibility


class BoardDetailResponse(BoardResponse):
    """Detailed board response with additional metadata."""

    card_count: int
    member_avatars: list[str]  # Up to 5 avatar URLs

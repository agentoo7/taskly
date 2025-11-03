"""Label schemas for request/response validation."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class LabelBase(BaseModel):
    """Base label schema."""

    name: str = Field(..., min_length=1, max_length=50, description="Label name")
    color: str = Field(..., pattern=r"^#[0-9A-Fa-f]{6}$", description="Hex color code (#RRGGBB)")


class LabelCreate(LabelBase):
    """Schema for creating a new label."""

    pass


class LabelUpdate(BaseModel):
    """Schema for updating a label."""

    name: str | None = Field(None, min_length=1, max_length=50, description="Label name")
    color: str | None = Field(
        None, pattern=r"^#[0-9A-Fa-f]{6}$", description="Hex color code (#RRGGBB)"
    )


class LabelResponse(LabelBase):
    """Schema for label response."""

    id: UUID
    workspace_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LabelAssignRequest(BaseModel):
    """Schema for assigning label to card."""

    label_id: UUID

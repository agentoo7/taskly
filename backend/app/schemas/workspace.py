"""Workspace Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class WorkspaceCreate(BaseModel):
    """Schema for creating a new workspace."""

    name: str = Field(..., min_length=1, max_length=100)

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        """Validate workspace name is not empty or whitespace."""
        if not v.strip():
            raise ValueError("Workspace name cannot be empty or whitespace")
        return v.strip()


class WorkspaceUpdate(BaseModel):
    """Schema for updating workspace."""

    name: str | None = Field(None, min_length=1, max_length=100)

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str | None) -> str | None:
        """Validate workspace name is not empty or whitespace if provided."""
        if v is not None and not v.strip():
            raise ValueError("Workspace name cannot be empty or whitespace")
        return v.strip() if v else None


class WorkspaceResponse(BaseModel):
    """Schema for workspace response."""

    id: UUID
    name: str
    created_by: UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WorkspaceDetailResponse(WorkspaceResponse):
    """Schema for detailed workspace response with boards and members."""

    boards: list[dict[str, Any]]
    members: list[dict[str, Any]]

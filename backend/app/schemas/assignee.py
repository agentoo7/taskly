"""Assignee schemas for request/response validation."""

from uuid import UUID

from pydantic import BaseModel


class AssigneeRequest(BaseModel):
    """Schema for assigning user to card."""

    user_id: UUID

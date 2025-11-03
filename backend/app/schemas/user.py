"""User schemas for request/response validation."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class UserResponse(BaseModel):
    """User response schema."""

    id: UUID
    username: str
    email: EmailStr
    avatar_url: str | None = None
    github_id: int

    model_config = ConfigDict(from_attributes=True)

"""Pydantic schemas for workspace invitations."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models.workspace_invitation import DeliveryStatusEnum
from app.models.workspace_member import RoleEnum


class InvitationCreate(BaseModel):
    """Schema for creating invitations."""

    emails: list[EmailStr] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="List of email addresses to invite (max 10)",
    )
    role: RoleEnum = Field(
        default=RoleEnum.MEMBER,
        description="Role to assign to invited members",
    )


class InvitationResponse(BaseModel):
    """Schema for invitation response."""

    id: UUID
    workspace_id: UUID
    email: str
    role: RoleEnum
    token: str
    invited_by: UUID
    delivery_status: DeliveryStatusEnum
    created_at: datetime
    expires_at: datetime
    accepted_at: datetime | None

    model_config = {"from_attributes": True}


class InvitationDetailResponse(BaseModel):
    """Schema for invitation details (public view for acceptance page)."""

    id: UUID
    workspace_id: UUID
    workspace_name: str | None = None
    email: str
    role: RoleEnum
    inviter_name: str | None = None
    inviter_avatar: str | None = None
    created_at: datetime
    expires_at: datetime
    is_expired: bool
    is_accepted: bool

    model_config = {"from_attributes": True}


class InvitationAcceptResponse(BaseModel):
    """Schema for successful invitation acceptance."""

    workspace_id: UUID
    user_id: UUID
    role: RoleEnum
    message: str = "Invitation accepted successfully"

    model_config = {"from_attributes": True}

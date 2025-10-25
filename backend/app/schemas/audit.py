"""Pydantic schemas for workspace audit logs."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel

from app.models.workspace_audit_log import AuditActionEnum


class AuditLogResponse(BaseModel):
    """Schema for audit log response."""

    id: UUID
    workspace_id: UUID
    actor_id: UUID
    action: AuditActionEnum
    resource_type: str
    resource_id: UUID
    context_data: dict[str, Any] | None
    created_at: datetime

    model_config = {"from_attributes": True}

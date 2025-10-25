"""Member API endpoints for managing workspace members."""

from datetime import datetime
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.models.workspace_audit_log import AuditActionEnum
from app.models.workspace_member import RoleEnum
from app.services.audit_service import AuditService
from app.services.workspace_service import WorkspaceService

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["members"])


class MemberResponse(BaseModel):
    """Schema for member response."""

    user_id: UUID
    username: str
    email: str
    avatar_url: str | None
    role: RoleEnum
    joined_at: datetime

    model_config = {"from_attributes": True}


class MemberRoleUpdate(BaseModel):
    """Schema for updating member role."""

    role: RoleEnum


@router.get("/api/workspaces/{workspace_id}/members", response_model=list[MemberResponse])
async def list_workspace_members(
    workspace_id: UUID,
    limit: int = 50,
    offset: int = 0,
    search: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[MemberResponse]:
    """
    List workspace members with pagination and search.

    Args:
        workspace_id: UUID of workspace
        limit: Maximum number of members to return (default 50)
        offset: Number of members to skip (default 0)
        search: Optional search term for filtering by name or email
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of workspace members

    Raises:
        HTTPException: 401 if not authenticated, 403 if not a member
    """
    from sqlalchemy import or_, select

    from app.models.workspace_member import WorkspaceMember

    service = WorkspaceService(db)

    # Check if user is member
    is_member = await service.check_workspace_member(workspace_id, UUID(str(current_user.id)))
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be a workspace member to view members",
        )

    # Build query
    query = (
        select(WorkspaceMember, User)
        .join(User, WorkspaceMember.user_id == User.id)
        .where(WorkspaceMember.workspace_id == workspace_id)
    )

    # Add search filter
    if search:
        search_term = f"%{search.lower()}%"
        query = query.where(
            or_(
                User.username.ilike(search_term),  # type: ignore[attr-defined]
                User.email.ilike(search_term),  # type: ignore[attr-defined]
            )
        )

    # Add pagination
    query = query.order_by(WorkspaceMember.joined_at.desc()).limit(limit).offset(offset)

    result = await db.execute(query)
    members_data = result.all()

    # Format response
    members = []
    for member, user in members_data:
        members.append(
            MemberResponse(
                user_id=UUID(str(user.id)),
                username=str(user.username),
                email=str(user.email),
                avatar_url=str(user.avatar_url) if user.avatar_url else None,
                role=member.role,  # type: ignore[arg-type]
                joined_at=member.joined_at,  # type: ignore[arg-type]
            )
        )

    return members


@router.patch("/api/workspaces/{workspace_id}/members/{user_id}")
async def update_member_role(
    workspace_id: UUID,
    user_id: UUID,
    data: MemberRoleUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """
    Update workspace member role (admin only).

    Prevents:
    - Last admin from changing their role to member
    - Non-admins from changing any roles

    Args:
        workspace_id: UUID of workspace
        user_id: UUID of member to update
        data: New role data
        current_user: Current authenticated user (must be admin)
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: 401 if not authenticated, 403 if not admin,
                      400 if trying to demote last admin
    """
    from uuid import UUID as UUIDType

    from sqlalchemy import and_, func, select, update

    from app.models.workspace_member import WorkspaceMember

    service = WorkspaceService(db)

    # Check if current user is admin
    await service._check_admin(workspace_id, UUIDType(str(current_user.id)))

    # Get current role of target user
    result = await db.execute(
        select(WorkspaceMember).where(
            and_(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id,
            )
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found in workspace",
        )

    # If changing from ADMIN to MEMBER, check if last admin
    if member.role == RoleEnum.ADMIN and data.role == RoleEnum.MEMBER:  # type: ignore[comparison-overlap]
        # Count total admins
        admin_count_result = await db.execute(
            select(func.count(WorkspaceMember.id)).where(
                and_(
                    WorkspaceMember.workspace_id == workspace_id,
                    WorkspaceMember.role == RoleEnum.ADMIN,
                )
            )
        )
        admin_count = admin_count_result.scalar() or 0

        if admin_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are the only admin. Promote another member first.",
            )

    # Store old role for audit
    old_role = member.role

    # Update role
    await db.execute(
        update(WorkspaceMember)
        .where(
            and_(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id,
            )
        )
        .values(role=data.role)
    )
    await db.commit()

    # Audit log
    audit_service = AuditService(db)
    await audit_service.log_action(
        workspace_id=workspace_id,
        actor_id=UUIDType(str(current_user.id)),
        action=AuditActionEnum.MEMBER_ROLE_CHANGED,
        resource_type="member",
        resource_id=user_id,
        context_data={
            "old_role": str(old_role),
            "new_role": data.role.value,
        },
    )

    # TODO: Broadcast WebSocket event member_role_changed with timestamp

    logger.info(
        "member.role.updated",
        workspace_id=str(workspace_id),
        user_id=str(user_id),
        new_role=data.role.value,
        actor_id=str(current_user.id),
    )

    return {"message": f"Member role updated to {data.role.value}"}


@router.delete(
    "/api/workspaces/{workspace_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_member(
    workspace_id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Remove member from workspace (admin only).

    Prevents:
    - Admin from removing themselves
    - Removing the last admin
    - Non-admins from removing anyone

    Args:
        workspace_id: UUID of workspace
        user_id: UUID of member to remove
        current_user: Current authenticated user (must be admin)
        db: Database session

    Raises:
        HTTPException: 401 if not authenticated, 403 if not admin,
                      400 if trying to remove self or last admin
    """
    from uuid import UUID as UUIDType

    from sqlalchemy import and_, delete, func, select

    from app.models.workspace_member import WorkspaceMember

    service = WorkspaceService(db)

    # Check if current user is admin
    await service._check_admin(workspace_id, UUIDType(str(current_user.id)))

    # Prevent removing self
    if user_id == UUIDType(str(current_user.id)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove yourself from workspace",
        )

    # Get member to remove
    result = await db.execute(
        select(WorkspaceMember).where(
            and_(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id,
            )
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found in workspace",
        )

    # If removing an admin, check if last admin
    if member.role == RoleEnum.ADMIN:  # type: ignore[comparison-overlap]
        admin_count_result = await db.execute(
            select(func.count(WorkspaceMember.id)).where(
                and_(
                    WorkspaceMember.workspace_id == workspace_id,
                    WorkspaceMember.role == RoleEnum.ADMIN,
                )
            )
        )
        admin_count = admin_count_result.scalar() or 0

        if admin_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove the last admin. Promote another member first.",
            )

    # Store member info for audit
    member_role = member.role

    # Remove member
    await db.execute(
        delete(WorkspaceMember).where(
            and_(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id,
            )
        )
    )
    await db.commit()

    # Audit log
    audit_service = AuditService(db)
    await audit_service.log_action(
        workspace_id=workspace_id,
        actor_id=UUIDType(str(current_user.id)),
        action=AuditActionEnum.MEMBER_REMOVED,
        resource_type="member",
        resource_id=user_id,
        context_data={"role": str(member_role)},
    )

    # TODO: Broadcast WebSocket event member_removed with timestamp

    logger.info(
        "member.removed",
        workspace_id=str(workspace_id),
        user_id=str(user_id),
        actor_id=str(current_user.id),
    )

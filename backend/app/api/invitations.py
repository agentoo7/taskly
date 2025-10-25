"""Invitation API endpoints for managing workspace invitations."""

from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_current_user_optional
from app.core.database import get_db
from app.models.user import User
from app.schemas.invitation import (
    InvitationAcceptResponse,
    InvitationCreate,
    InvitationDetailResponse,
    InvitationResponse,
)
from app.services.invitation_service import InvitationService

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["invitations"])


@router.post(
    "/api/workspaces/{workspace_id}/invitations",
    response_model=list[InvitationResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_invitations(
    workspace_id: UUID,
    data: InvitationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[InvitationResponse]:
    """
    Create workspace invitations (admin only).

    Sends invitation emails to the specified addresses. Skips users who are
    already members or have pending invitations.

    Rate limiting: Max 50 invitations per workspace per hour (TODO: implement in future iteration).
    Max 10 emails per request (enforced by schema validation).

    Args:
        workspace_id: UUID of workspace to invite users to
        data: Invitation creation data with emails and role
        current_user: Current authenticated user (must be admin)
        db: Database session

    Returns:
        List of created invitations

    Raises:
        HTTPException: 401 if not authenticated, 403 if not admin, 400 if validation fails
    """
    service = InvitationService(db)

    # Create invitations
    from uuid import UUID as UUIDType

    invitations = await service.create_invitations(
        workspace_id=workspace_id,
        emails=data.emails,
        role=data.role,
        inviter_id=UUIDType(str(current_user.id)),
    )

    # Trigger email sending for each invitation (Task 4)
    for invitation in invitations:
        await service.send_invitation_email(UUIDType(str(invitation.id)))

    logger.info(
        "api.invitations.create.success",
        workspace_id=str(workspace_id),
        invitation_count=len(invitations),
        user_id=str(current_user.id),
    )

    return [InvitationResponse.model_validate(inv) for inv in invitations]


@router.get(
    "/api/invitations/{token}",
    response_model=InvitationDetailResponse,
)
async def get_invitation(
    token: str,
    current_user: User | None = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
) -> InvitationDetailResponse:
    """
    Get invitation details by token (public endpoint for acceptance page).

    Args:
        token: Invitation token
        current_user: Optional current user (for acceptance page UI)
        db: Database session

    Returns:
        Invitation details with workspace and inviter information

    Raises:
        HTTPException: 404 if invitation not found
    """
    service = InvitationService(db)
    invitation = await service.get_invitation_by_token(token)

    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found",
        )

    # Build response with additional details
    # Note: In production, we'd use relationships to load workspace and inviter
    # For now, we'll return basic details
    return InvitationDetailResponse(
        id=invitation.id,  # type: ignore[arg-type]
        workspace_id=invitation.workspace_id,  # type: ignore[arg-type]
        workspace_name=None,  # TODO: Load from relationship
        email=str(invitation.email),
        role=invitation.role,  # type: ignore[arg-type]
        inviter_name=None,  # TODO: Load from relationship
        inviter_avatar=None,  # TODO: Load from relationship
        created_at=invitation.created_at,  # type: ignore[arg-type]
        expires_at=invitation.expires_at,  # type: ignore[arg-type]
        is_expired=invitation.is_expired,
        is_accepted=invitation.is_accepted,
    )


@router.post(
    "/api/invitations/{token}/accept",
    response_model=InvitationAcceptResponse,
)
async def accept_invitation(
    token: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> InvitationAcceptResponse:
    """
    Accept workspace invitation (authenticated users only).

    Args:
        token: Invitation token
        current_user: Current authenticated user
        db: Database session

    Returns:
        Acceptance confirmation with workspace and role details

    Raises:
        HTTPException: 401 if not authenticated, 404 if not found,
                      400 if expired/accepted, 403 if email mismatch
    """
    from uuid import UUID as UUIDType

    service = InvitationService(db)

    member = await service.accept_invitation(token, UUIDType(str(current_user.id)))

    # TODO: Task 7 - Broadcast WebSocket event member_joined with timestamp

    logger.info(
        "api.invitations.accept.success",
        workspace_id=str(member.workspace_id),
        user_id=str(current_user.id),
        role=str(member.role),
    )

    return InvitationAcceptResponse(
        workspace_id=UUIDType(str(member.workspace_id)),
        user_id=UUIDType(str(member.user_id)),
        role=member.role,  # type: ignore[arg-type]
    )


@router.delete(
    "/api/workspaces/{workspace_id}/invitations/{invitation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def revoke_invitation(
    workspace_id: UUID,
    invitation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Revoke (delete) pending invitation (admin only).

    Args:
        workspace_id: UUID of workspace
        invitation_id: UUID of invitation to revoke
        current_user: Current authenticated user (must be admin)
        db: Database session

    Raises:
        HTTPException: 401 if not authenticated, 403 if not admin, 404 if not found
    """
    from uuid import UUID as UUIDType

    service = InvitationService(db)
    await service.revoke_invitation(invitation_id, UUIDType(str(current_user.id)))

    logger.info(
        "api.invitations.revoke.success",
        workspace_id=str(workspace_id),
        invitation_id=str(invitation_id),
        user_id=str(current_user.id),
    )


@router.post(
    "/api/workspaces/{workspace_id}/invitations/{invitation_id}/resend",
    response_model=InvitationResponse,
)
async def resend_invitation(
    workspace_id: UUID,
    invitation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> InvitationResponse:
    """
    Resend invitation with new token (admin only).

    Generates a new token, updates expiration date, and sends a new email.

    Args:
        workspace_id: UUID of workspace
        invitation_id: UUID of invitation to resend
        current_user: Current authenticated user (must be admin)
        db: Database session

    Returns:
        Updated invitation with new token

    Raises:
        HTTPException: 401 if not authenticated, 403 if not admin,
                      404 if not found, 400 if already accepted
    """
    from uuid import UUID as UUIDType

    service = InvitationService(db)
    invitation = await service.resend_invitation(invitation_id, UUIDType(str(current_user.id)))

    # Trigger email sending (Task 4)
    await service.send_invitation_email(UUIDType(str(invitation.id)))

    logger.info(
        "api.invitations.resend.success",
        workspace_id=str(workspace_id),
        invitation_id=str(invitation_id),
        user_id=str(current_user.id),
    )

    return InvitationResponse.model_validate(invitation)


@router.get(
    "/api/workspaces/{workspace_id}/invitations",
    response_model=list[InvitationResponse],
)
async def list_workspace_invitations(
    workspace_id: UUID,
    include_accepted: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[InvitationResponse]:
    """
    List all invitations for a workspace (admin only).

    Args:
        workspace_id: UUID of workspace
        include_accepted: Whether to include accepted invitations
        current_user: Current authenticated user (must be admin)
        db: Database session

    Returns:
        List of invitations

    Raises:
        HTTPException: 401 if not authenticated, 403 if not admin
    """
    from uuid import UUID as UUIDType

    service = InvitationService(db)

    # Check admin permission
    await service._check_admin(workspace_id, UUIDType(str(current_user.id)))

    invitations = await service.get_workspace_invitations(workspace_id, include_accepted)

    return [InvitationResponse.model_validate(inv) for inv in invitations]

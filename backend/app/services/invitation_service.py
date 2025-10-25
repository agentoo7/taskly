"""Invitation service for managing workspace invitations."""

from datetime import datetime
from uuid import UUID

import structlog
from fastapi import HTTPException, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.workspace_audit_log import AuditActionEnum
from app.models.workspace_invitation import DeliveryStatusEnum, WorkspaceInvitation
from app.models.workspace_member import RoleEnum, WorkspaceMember
from app.services.audit_service import AuditService

logger = structlog.get_logger(__name__)


class InvitationService:
    """Service for handling workspace invitation operations."""

    def __init__(self, db: AsyncSession):
        """
        Initialize InvitationService.

        Args:
            db: Async database session
        """
        self.db = db

    async def create_invitations(
        self,
        workspace_id: UUID,
        emails: list[str],
        role: RoleEnum,
        inviter_id: UUID,
    ) -> list[WorkspaceInvitation]:
        """
        Create and send invitations to multiple emails.

        Args:
            workspace_id: UUID of workspace to invite users to
            emails: List of email addresses to invite
            role: Role to assign (MEMBER or ADMIN)
            inviter_id: UUID of user creating invitations

        Returns:
            List of created invitation objects

        Raises:
            HTTPException: 403 if inviter is not admin, 400 if validation fails
        """
        logger.info(
            "invitation.create.start",
            workspace_id=str(workspace_id),
            email_count=len(emails),
            role=role.value,
            inviter_id=str(inviter_id),
        )

        # Verify inviter is admin
        await self._check_admin(workspace_id, inviter_id)

        invitations = []

        for email in emails:
            email_lower = email.lower().strip()

            # Check if user already member
            existing_member = await self.db.execute(
                select(WorkspaceMember)
                .join(User, WorkspaceMember.user_id == User.id)
                .where(
                    and_(
                        WorkspaceMember.workspace_id == workspace_id,
                        func.lower(User.email) == email_lower,
                    )
                )
            )
            if existing_member.scalar_one_or_none():
                logger.info(
                    "invitation.skipped.already_member",
                    workspace_id=str(workspace_id),
                    email=email_lower,
                )
                continue  # Skip already-member emails

            # Check if invitation already exists
            existing_invite = await self.db.execute(
                select(WorkspaceInvitation).where(
                    and_(
                        WorkspaceInvitation.workspace_id == workspace_id,
                        func.lower(WorkspaceInvitation.email) == email_lower,
                        WorkspaceInvitation.accepted_at.is_(None),
                    )
                )
            )
            if existing_invite.scalar_one_or_none():
                logger.info(
                    "invitation.skipped.pending_exists",
                    workspace_id=str(workspace_id),
                    email=email_lower,
                )
                continue  # Skip if pending invitation exists

            # Create invitation
            invitation = WorkspaceInvitation(
                workspace_id=workspace_id,
                email=email_lower,
                role=role,
                invited_by=inviter_id,
            )
            self.db.add(invitation)
            invitations.append(invitation)

        await self.db.commit()

        # Refresh all invitations to get generated fields
        for invitation in invitations:
            await self.db.refresh(invitation)

        # Audit log for each invitation
        audit_service = AuditService(self.db)
        for invitation in invitations:
            await audit_service.log_action(
                workspace_id=workspace_id,
                actor_id=inviter_id,
                action=AuditActionEnum.INVITATION_CREATED,
                resource_type="invitation",
                resource_id=UUID(str(invitation.id)),
                context_data={
                    "email": invitation.email,
                    "role": invitation.role.value,
                },
            )

        logger.info(
            "invitation.create.success",
            workspace_id=str(workspace_id),
            created_count=len(invitations),
            inviter_id=str(inviter_id),
        )

        # Note: Email sending will be triggered from API layer using Celery task
        return invitations

    async def send_invitation_email(self, invitation_id: UUID) -> None:
        """
        Enqueue email send job for invitation.

        Args:
            invitation_id: UUID of invitation to send email for
        """
        # Import here to avoid circular dependency with celery tasks
        from app.tasks.send_invitation_email import send_invitation_email_task

        # Enqueue Celery task (will run in background worker)
        send_invitation_email_task.delay(str(invitation_id))

        logger.info(
            "invitation.email.enqueued",
            invitation_id=str(invitation_id),
        )

    async def get_invitation_by_token(self, token: str) -> WorkspaceInvitation | None:
        """
        Get invitation by token.

        Args:
            token: Invitation token

        Returns:
            WorkspaceInvitation if found, None otherwise
        """
        result = await self.db.execute(
            select(WorkspaceInvitation).where(WorkspaceInvitation.token == token)
        )
        return result.scalar_one_or_none()

    async def accept_invitation(self, token: str, user_id: UUID) -> WorkspaceMember:
        """
        Accept invitation and add user to workspace.

        Args:
            token: Invitation token
            user_id: UUID of user accepting invitation

        Returns:
            Created WorkspaceMember record

        Raises:
            HTTPException: 404 if not found, 400 if expired/accepted, 403 if email mismatch
        """
        logger.info(
            "invitation.accept.start",
            token=token[:8] + "...",
            user_id=str(user_id),
        )

        # Find invitation
        invitation = await self.get_invitation_by_token(token)

        if not invitation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invitation not found",
            )

        # Check if expired
        if invitation.is_expired:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invitation has expired. Please request a new invitation.",
            )

        # Check if already accepted
        if invitation.is_accepted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invitation already accepted",
            )

        # Get user
        user = await self.db.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        # Check if user's email matches invitation email
        if user.email.lower() != invitation.email.lower():
            error_msg = (
                f"This invitation was sent to {invitation.email}. "
                f"Your account uses {user.email}."
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "type": "email_mismatch",
                    "message": error_msg,
                    "invitation_email": invitation.email,
                    "user_email": user.email,
                },
            )

        # Check if user already member
        existing = await self.db.execute(
            select(WorkspaceMember).where(
                and_(
                    WorkspaceMember.workspace_id == invitation.workspace_id,
                    WorkspaceMember.user_id == user_id,
                )
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Already a workspace member",
            )

        # Add user to workspace
        from sqlalchemy.orm import attributes

        member = WorkspaceMember(
            workspace_id=UUID(str(invitation.workspace_id)),
            user_id=user_id,
            role=invitation.role,  # type: ignore[arg-type]
        )
        self.db.add(member)

        # Mark invitation as accepted
        attributes.set_attribute(invitation, "accepted_at", datetime.utcnow())

        await self.db.commit()
        await self.db.refresh(member)

        # Audit log
        audit_service = AuditService(self.db)
        await audit_service.log_action(
            workspace_id=UUID(str(invitation.workspace_id)),
            actor_id=user_id,
            action=AuditActionEnum.INVITATION_ACCEPTED,
            resource_type="invitation",
            resource_id=UUID(str(invitation.id)),
            context_data={
                "email": invitation.email,
                "role": invitation.role.value,
            },
        )

        logger.info(
            "invitation.accept.success",
            workspace_id=str(invitation.workspace_id),
            user_id=str(user_id),
            role=invitation.role.value,
        )

        return member

    async def revoke_invitation(self, invitation_id: UUID, admin_id: UUID) -> None:
        """
        Revoke (delete) invitation.

        Args:
            invitation_id: UUID of invitation to revoke
            admin_id: UUID of admin revoking invitation

        Raises:
            HTTPException: 404 if not found, 403 if not admin
        """
        invitation = await self.db.get(WorkspaceInvitation, invitation_id)

        if not invitation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invitation not found",
            )

        # Verify admin permission
        await self._check_admin(UUID(str(invitation.workspace_id)), admin_id)

        # Audit log before deletion
        audit_service = AuditService(self.db)
        await audit_service.log_action(
            workspace_id=UUID(str(invitation.workspace_id)),
            actor_id=admin_id,
            action=AuditActionEnum.INVITATION_REVOKED,
            resource_type="invitation",
            resource_id=invitation_id,
            context_data={"email": invitation.email},
        )

        await self.db.delete(invitation)
        await self.db.commit()

        logger.info(
            "invitation.revoke.success",
            invitation_id=str(invitation_id),
            workspace_id=str(invitation.workspace_id),
            admin_id=str(admin_id),
        )

    async def resend_invitation(self, invitation_id: UUID, admin_id: UUID) -> WorkspaceInvitation:
        """
        Resend invitation by generating new token and sending new email.

        Args:
            invitation_id: UUID of invitation to resend
            admin_id: UUID of admin requesting resend

        Returns:
            Updated invitation with new token

        Raises:
            HTTPException: 404 if not found, 403 if not admin, 400 if already accepted
        """
        invitation = await self.db.get(WorkspaceInvitation, invitation_id)

        if not invitation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invitation not found",
            )

        # Verify admin permission
        await self._check_admin(UUID(str(invitation.workspace_id)), admin_id)

        # Check not already accepted
        if invitation.is_accepted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot resend accepted invitation",
            )

        # Generate new token
        import secrets
        from datetime import timedelta

        # Update invitation fields
        new_token = secrets.token_urlsafe(32)
        new_expires_at = datetime.utcnow() + timedelta(days=7)

        # Use setattr to avoid mypy Column assignment issues
        from sqlalchemy.orm import attributes

        attributes.set_attribute(invitation, "token", new_token)
        attributes.set_attribute(invitation, "expires_at", new_expires_at)
        attributes.set_attribute(invitation, "delivery_status", DeliveryStatusEnum.PENDING)

        await self.db.commit()
        await self.db.refresh(invitation)

        # Audit log
        audit_service = AuditService(self.db)
        await audit_service.log_action(
            workspace_id=UUID(str(invitation.workspace_id)),
            actor_id=admin_id,
            action=AuditActionEnum.INVITATION_RESENT,
            resource_type="invitation",
            resource_id=invitation_id,
            context_data={"email": invitation.email},
        )

        logger.info(
            "invitation.resend.success",
            invitation_id=str(invitation_id),
            workspace_id=str(invitation.workspace_id),
            admin_id=str(admin_id),
        )

        # Note: Email sending will be triggered from API layer
        return invitation

    async def get_workspace_invitations(
        self, workspace_id: UUID, include_accepted: bool = False
    ) -> list[WorkspaceInvitation]:
        """
        Get all invitations for a workspace.

        Args:
            workspace_id: UUID of workspace
            include_accepted: Whether to include accepted invitations

        Returns:
            List of invitations
        """
        query = select(WorkspaceInvitation).where(WorkspaceInvitation.workspace_id == workspace_id)

        if not include_accepted:
            query = query.where(WorkspaceInvitation.accepted_at.is_(None))

        result = await self.db.execute(query.order_by(WorkspaceInvitation.created_at.desc()))
        return list(result.scalars().all())

    async def _check_admin(self, workspace_id: UUID, user_id: UUID) -> None:
        """
        Verify user is workspace admin.

        Args:
            workspace_id: UUID of workspace
            user_id: UUID of user to check

        Raises:
            HTTPException: 403 if user is not admin
        """
        result = await self.db.execute(
            select(WorkspaceMember).where(
                and_(
                    WorkspaceMember.workspace_id == workspace_id,
                    WorkspaceMember.user_id == user_id,
                    WorkspaceMember.role == RoleEnum.ADMIN,
                )
            )
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Must be workspace admin to perform this action",
            )

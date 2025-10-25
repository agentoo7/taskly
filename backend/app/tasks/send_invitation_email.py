"""Celery task for sending invitation emails."""

import asyncio
from datetime import datetime
from pathlib import Path

import structlog
from celery import shared_task
from jinja2 import Environment, FileSystemLoader
from sqlalchemy import select

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.workspace_invitation import DeliveryStatusEnum, WorkspaceInvitation

logger = structlog.get_logger(__name__)


@shared_task(bind=True, time_limit=30, soft_time_limit=25, max_retries=3)
def send_invitation_email_task(self, invitation_id: str) -> dict[str, str]:
    """
    Send invitation email via SendGrid.

    This task runs asynchronously via Celery. It includes:
    - Retry logic with exponential backoff (max 3 retries)
    - Timeout protection (30s hard limit, 25s soft limit)
    - Delivery status tracking
    - Structured logging with correlation IDs

    Args:
        invitation_id: UUID string of invitation to send email for

    Returns:
        dict with status and message

    Raises:
        Exception: Re-raises after max retries exceeded
    """
    try:
        # Run async database operations in event loop
        result = asyncio.run(_send_invitation_email(invitation_id))
        return result
    except Exception as exc:
        logger.error(
            "invitation.email.failed",
            invitation_id=invitation_id,
            error=str(exc),
            error_type=type(exc).__name__,
            retry_count=self.request.retries,
        )

        # Retry with exponential backoff: 60s, 120s, 240s
        raise self.retry(exc=exc, countdown=60 * (2**self.request.retries))


async def _send_invitation_email(invitation_id: str) -> dict[str, str]:
    """
    Internal async function to send invitation email.

    Args:
        invitation_id: UUID string of invitation

    Returns:
        dict with status and message
    """
    async with AsyncSessionLocal() as db:
        # Load invitation with relationships
        result = await db.execute(
            select(WorkspaceInvitation).where(WorkspaceInvitation.id == invitation_id)
        )
        invitation = result.scalar_one_or_none()

        if not invitation:
            logger.warning("invitation.email.not_found", invitation_id=invitation_id)
            return {"status": "error", "message": "Invitation not found"}

        # Load template
        template_dir = Path(__file__).parent.parent / "templates" / "emails"
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template("workspace_invitation.html")

        # Render email HTML
        # Note: In production, we'd load workspace and inviter via relationships
        # For now, we'll use placeholder data
        html_content = template.render(
            workspace_name="Workspace",  # TODO: Load from relationship
            inviter_name="Team Admin",  # TODO: Load from relationship
            inviter_avatar=None,  # TODO: Load from relationship
            role=str(invitation.role.value).title(),
            invitation_url=f"{settings.APP_URL}/invitations/{invitation.token}",
            expires_at=invitation.expires_at.strftime("%B %d, %Y at %I:%M %p UTC"),
            app_url=settings.APP_URL,
            year=datetime.now().year,
        )

        # Send email
        if settings.SENDGRID_API_KEY:
            # Production: Send via SendGrid
            try:
                from sendgrid import SendGridAPIClient
                from sendgrid.helpers.mail import Content, Email, Mail, To

                message = Mail(
                    from_email=Email(settings.FROM_EMAIL, settings.FROM_NAME),
                    to_emails=To(str(invitation.email)),
                    subject="You're invited to join a workspace on Taskly",
                    html_content=Content("text/html", html_content),
                )

                sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
                response = sg.send(message)

                # Update delivery status
                from sqlalchemy.orm import attributes

                attributes.set_attribute(invitation, "delivery_status", DeliveryStatusEnum.SENT)
                await db.commit()

                logger.info(
                    "invitation.email.sent",
                    invitation_id=invitation_id,
                    email=str(invitation.email),
                    status_code=response.status_code,
                )

                return {
                    "status": "sent",
                    "message": f"Email sent to {invitation.email}",
                }

            except Exception as e:
                # Update delivery status to FAILED
                from sqlalchemy.orm import attributes

                attributes.set_attribute(invitation, "delivery_status", DeliveryStatusEnum.FAILED)
                await db.commit()

                logger.error(
                    "invitation.email.sendgrid_error",
                    invitation_id=invitation_id,
                    error=str(e),
                )
                raise

        else:
            # Development: Log email to console
            preview_url = f"{settings.APP_URL}/invitations/{invitation.token}"
            logger.info(
                "invitation.email.dev_mode",
                invitation_id=invitation_id,
                to=str(invitation.email),
                subject="Workspace Invitation",
                preview_url=preview_url,
            )

            print("\n" + "=" * 80)
            print("📧 EMAIL PREVIEW (Development Mode)")
            print("=" * 80)
            print(f"To: {invitation.email}")
            print("Subject: You're invited to join a workspace on Taskly")
            print(f"Invitation URL: {preview_url}")
            print("=" * 80)
            print(html_content)
            print("=" * 80 + "\n")

            # Update delivery status to SENT (in dev mode)
            from sqlalchemy.orm import attributes

            attributes.set_attribute(invitation, "delivery_status", DeliveryStatusEnum.SENT)
            await db.commit()

            return {
                "status": "dev_logged",
                "message": f"Email logged to console for {invitation.email}",
            }

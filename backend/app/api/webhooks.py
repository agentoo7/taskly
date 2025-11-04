"""Webhook endpoints for external service callbacks."""

import os
from typing import Any

import structlog
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sendgrid.helpers.eventwebhook import EventWebhook
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.workspace_invitation import DeliveryStatusEnum, WorkspaceInvitation

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["webhooks"])


def _verify_sendgrid_signature(
    public_key: str,
    payload: bytes,
    signature: str,
    timestamp: str,
) -> bool:
    """
    Verify SendGrid webhook signature using ECDSA.

    Args:
        public_key: SendGrid public key (PEM format)
        payload: Raw request body
        signature: Signature from X-Twilio-Email-Event-Webhook-Signature header
        timestamp: Timestamp from X-Twilio-Email-Event-Webhook-Timestamp header

    Returns:
        True if signature is valid, False otherwise
    """
    try:
        event_webhook = EventWebhook()
        ec_public_key = event_webhook.convert_public_key_to_ecdsa(public_key)
        return event_webhook.verify_signature(
            ec_public_key,
            payload,
            signature,
            timestamp,
        )
    except Exception as e:
        logger.error(
            "webhook.sendgrid.signature_verification_error",
            error=str(e),
        )
        return False


@router.post("/api/webhooks/sendgrid", status_code=status.HTTP_200_OK)
async def sendgrid_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    x_twilio_email_event_webhook_signature: str | None = Header(None),
    x_twilio_email_event_webhook_timestamp: str | None = Header(None),
) -> dict[str, str]:
    """
    Handle SendGrid event webhooks for email delivery status updates.

    SendGrid sends POST requests to this endpoint when email events occur
    (delivered, bounced, etc.). Updates invitation delivery_status accordingly.

    Security: Verifies webhook signature using SendGrid's public key to prevent
    unauthorized requests and data poisoning attacks.

    Args:
        request: FastAPI request object containing event data
        db: Database session
        x_twilio_email_event_webhook_signature: SendGrid signature header
        x_twilio_email_event_webhook_timestamp: SendGrid timestamp header

    Returns:
        Success confirmation message

    Raises:
        HTTPException: 400 if event data is invalid
        HTTPException: 403 if signature verification fails
    """
    # Get SendGrid public key from environment
    public_key = os.getenv("SENDGRID_WEBHOOK_PUBLIC_KEY")

    # Verify signature if public key is configured
    if public_key:
        if not x_twilio_email_event_webhook_signature or not x_twilio_email_event_webhook_timestamp:
            logger.warning("webhook.sendgrid.missing_signature_headers")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Missing required signature headers",
            )

        # Get raw request body for signature verification
        body = await request.body()

        if not _verify_sendgrid_signature(
            public_key,
            body,
            x_twilio_email_event_webhook_signature,
            x_twilio_email_event_webhook_timestamp,
        ):
            logger.warning("webhook.sendgrid.invalid_signature")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid webhook signature",
            )

        logger.info("webhook.sendgrid.signature_verified")
    else:
        # In development/testing, allow webhooks without signature verification
        # but log a warning
        logger.warning(
            "webhook.sendgrid.signature_verification_disabled",
            message="SENDGRID_WEBHOOK_PUBLIC_KEY not configured - accepting all webhooks",
        )

    # Parse JSON payload
    try:
        events = await request.json()
    except Exception as e:
        logger.error("webhook.sendgrid.invalid_json", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload",
        ) from e

    # Process each event in the batch
    processed = 0
    for event in events if isinstance(events, list) else [events]:
        await _process_sendgrid_event(event, db)
        processed += 1

    logger.info(
        "webhook.sendgrid.batch_processed",
        event_count=processed,
    )

    return {"status": "success", "processed": processed}


async def _process_sendgrid_event(event: dict[str, Any], db: AsyncSession) -> None:
    """
    Process a single SendGrid event and update invitation delivery status.

    Args:
        event: SendGrid event data
        db: Database session
    """
    event_type = event.get("event")
    invitation_id_str = event.get("invitation_id")  # Custom field we'll add to emails

    if not event_type or not invitation_id_str:
        logger.warning(
            "webhook.sendgrid.missing_fields",
            event_type=event_type,
            has_invitation_id=bool(invitation_id_str),
        )
        return

    # Map SendGrid events to our DeliveryStatusEnum
    status_mapping = {
        "processed": DeliveryStatusEnum.SENT,
        "delivered": DeliveryStatusEnum.DELIVERED,
        "bounce": DeliveryStatusEnum.BOUNCED,
        "dropped": DeliveryStatusEnum.FAILED,
        "deferred": None,  # Temporary failure, don't update status
    }

    new_status = status_mapping.get(event_type)
    if new_status is None:
        logger.debug(
            "webhook.sendgrid.event_ignored",
            event_type=event_type,
            invitation_id=invitation_id_str,
        )
        return

    # Find and update invitation
    try:
        from uuid import UUID

        invitation_id = UUID(invitation_id_str)
    except ValueError:
        logger.error(
            "webhook.sendgrid.invalid_uuid",
            invitation_id_str=invitation_id_str,
        )
        return

    result = await db.execute(
        select(WorkspaceInvitation).where(WorkspaceInvitation.id == invitation_id)
    )
    invitation = result.scalar_one_or_none()

    if not invitation:
        logger.warning(
            "webhook.sendgrid.invitation_not_found",
            invitation_id=str(invitation_id),
        )
        return

    # Update delivery status
    from sqlalchemy.orm import attributes

    attributes.set_attribute(invitation, "delivery_status", new_status)
    await db.commit()

    logger.info(
        "webhook.sendgrid.status_updated",
        invitation_id=str(invitation_id),
        event_type=event_type,
        new_status=new_status.value,
        email=invitation.email,
    )

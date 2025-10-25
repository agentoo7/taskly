"""Celery periodic task for cleaning up expired invitations."""

import asyncio
from datetime import datetime, timedelta

import structlog
from sqlalchemy import and_, delete

from app.core.database import AsyncSessionLocal
from app.models.workspace_invitation import WorkspaceInvitation
from app.tasks.celery_app import celery_app

logger = structlog.get_logger(__name__)


@celery_app.task
def cleanup_expired_invitations() -> dict[str, int]:
    """
    Delete expired unaccepted invitations older than 30 days.

    This task runs daily via Celery Beat. It removes invitations that:
    - Have expired (expires_at < now())
    - Have not been accepted (accepted_at IS NULL)
    - Are older than 30 days retention period

    Returns:
        dict with deleted_count
    """
    # Create fresh event loop for Celery worker
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(_cleanup_expired_invitations())
        return result
    finally:
        loop.close()


async def _cleanup_expired_invitations() -> dict[str, int]:
    """
    Internal async function to delete expired invitations.

    Returns:
        dict with deleted_count
    """
    async with AsyncSessionLocal() as db:
        # Calculate cutoff date (30 days ago)
        cutoff_date = datetime.utcnow() - timedelta(days=30)

        logger.info(
            "invitation.cleanup.start",
            cutoff_date=cutoff_date.isoformat(),
        )

        # Delete expired unaccepted invitations older than 30 days
        result = await db.execute(
            delete(WorkspaceInvitation).where(
                and_(
                    WorkspaceInvitation.expires_at < cutoff_date,
                    WorkspaceInvitation.accepted_at.is_(None),
                )
            )
        )

        deleted_count = result.rowcount or 0
        await db.commit()

        logger.info(
            "invitation.cleanup.complete",
            deleted_count=deleted_count,
            cutoff_date=cutoff_date.isoformat(),
        )

        return {"deleted_count": deleted_count}

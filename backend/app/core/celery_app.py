"""Celery application configuration."""

from celery import Celery

from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "taskly",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.send_invitation_email", "app.tasks.cleanup_invitations"],
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30,  # 30 seconds max per task
    task_soft_time_limit=25,  # Soft limit at 25 seconds
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)

# Beat schedule for periodic tasks (Task 14 - cleanup job)
celery_app.conf.beat_schedule = {
    "cleanup-expired-invitations": {
        "task": "app.tasks.cleanup_invitations.cleanup_expired_invitations",
        "schedule": 86400.0,  # Run daily (86400 seconds = 24 hours)
        "options": {"expires": 3600},  # Task expires after 1 hour if not executed
    },
}

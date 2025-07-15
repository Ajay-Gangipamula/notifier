from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "notification_orchestrator",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.workers.notification_tasks",
        "app.workers.event_tasks",
        "app.workers.analytics_tasks"
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Retry configuration
celery_app.conf.task_routes = {
    "app.workers.notification_tasks.send_notification": {"queue": "notifications"},
    "app.workers.event_tasks.process_event": {"queue": "events"},
    "app.workers.analytics_tasks.update_stats": {"queue": "analytics"},
}

# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    "process-pending-notifications": {
        "task": "app.workers.notification_tasks.process_pending_notifications",
        "schedule": 60.0,  # Every minute
    },
    "retry-failed-notifications": {
        "task": "app.workers.notification_tasks.retry_failed_notifications",
        "schedule": 300.0,  # Every 5 minutes
    },
    "update-daily-stats": {
        "task": "app.workers.analytics_tasks.update_daily_stats",
        "schedule": 3600.0,  # Every hour
    },
}
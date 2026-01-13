"""
Celery configuration for async task processing
"""

from celery import Celery

from backend.config import get_settings

settings = get_settings()

# Create Celery app
celery_app = Celery(
    "digestible", broker=settings.redis_url, backend=settings.redis_url, include=["backend.tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max per task
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_disable_rate_limits=False,
)

if __name__ == "__main__":
    celery_app.start()

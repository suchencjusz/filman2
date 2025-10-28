import os

from celery import Celery

# Get Redis URL from environment variable, default to localhost
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app instance
celery_app = Celery(
    "filman_server",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["filman_server.tasks"],
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
)

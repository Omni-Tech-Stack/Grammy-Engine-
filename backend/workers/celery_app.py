"""
Celery application configuration for async task processing
"""
from celery import Celery
import os

# Redis configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Initialize Celery app
celery_app = Celery(
    "grammy_engine",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "workers.song_tasks",
        "workers.mix_tasks",
        "workers.meter_tasks"
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
    task_time_limit=3600,  # 1 hour max
    task_soft_time_limit=3300,  # 55 minutes soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    result_expires=86400,  # 24 hours
)

# Task routing
celery_app.conf.task_routes = {
    "workers.song_tasks.*": {"queue": "song_generation"},
    "workers.mix_tasks.*": {"queue": "mixing"},
    "workers.meter_tasks.*": {"queue": "analysis"},
}

# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    "cleanup-old-tasks": {
        "task": "workers.song_tasks.cleanup_old_files",
        "schedule": 3600.0,  # Every hour
    },
}

if __name__ == "__main__":
    celery_app.start()

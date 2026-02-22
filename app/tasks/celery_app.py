from celery import Celery
from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "bot",
    broker=settings.celery_broker_url,
    include=[
        "app.tasks.subscription_expiry",
        "app.tasks.after_payment",
        "app.tasks.broadcast_tasks",
        "app.tasks.scenario_delayed",
    ],
)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
)
celery_app.conf.beat_schedule = {
    "expire-subscriptions-daily": {
        "task": "app.tasks.subscription_expiry.expire_subscriptions",
        "schedule": 86400.0,
    },
}

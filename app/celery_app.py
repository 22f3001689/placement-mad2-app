"""Celery app factory, wired to the Flask app context.

Run with `celery -A app.celery_app worker` / `celery -A app.celery_app beat`
(see Makefile's celery-worker/celery-beat targets).
"""

from celery import Celery, Task


def make_celery(flask_app):
    class FlaskTask(Task):
        def __call__(self, *args, **kwargs):
            with flask_app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(flask_app.import_name, task_cls=FlaskTask)
    celery_app.conf.update(
        broker_url=flask_app.config["REDIS_URL"],
        result_backend=flask_app.config["REDIS_URL"],
        broker_connection_retry_on_startup=True,
        # A .delay() call must fail fast (not hang/retry) when Redis is down,
        # so a route can return 503 immediately instead of blocking the request.
        broker_connection_timeout=2,
        task_publish_retry=False,
        # Job status is tracked via ExportJob.status, not Celery's result
        # backend - ignoring results also skips the backend's own pubsub
        # reconnect-with-backoff logic that .delay() would otherwise hit.
        task_ignore_result=True,
        beat_schedule={
            "send-interview-reminders": {
                "task": "app.tasks.send_interview_reminders",
                "schedule": 15 * 60,
            },
            "generate-placement-reports": {
                "task": "app.tasks.generate_placement_reports",
                "schedule": 24 * 60 * 60,
            },
        },
    )
    celery_app.set_default()
    flask_app.extensions["celery"] = celery_app
    return celery_app


from app import create_app

celery = make_celery(create_app())

# Task modules are registered by importing them once the Celery app exists.
import app.tasks  # noqa: F401

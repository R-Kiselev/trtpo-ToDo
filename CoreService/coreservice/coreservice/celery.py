import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "coreservice.settings")
app = Celery("coreservice")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


app.conf.beat_schedule = {
    "send_reports": {
        "task": "projects.tasks.send_reports_to_owners",
        "schedule": crontab(minute=0),
    },
}

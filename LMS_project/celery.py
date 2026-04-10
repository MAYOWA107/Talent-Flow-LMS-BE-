import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "LMS_project.settings")

app = Celery("LMS_project")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()


# celery -A farm_dash worker --pool=solo --loglevel=info

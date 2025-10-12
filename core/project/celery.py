"""
Документация:
https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html

Команда запуска:
make celery
"""

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "core.project.settings",
)

app = Celery("core.project")

app.config_from_object(
    "django.conf:settings",
    namespace="CELERY",
)

app.autodiscover_tasks()

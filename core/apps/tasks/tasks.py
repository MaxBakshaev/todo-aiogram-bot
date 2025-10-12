"""
Документация:
https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html
"""

from celery import shared_task
from .models import Task


@shared_task
def send_task_reminder(name):
    """Отправка уведомлений."""

    try:
        task = Task.objects.get(name=name)
        print(f"[Celery] Напоминание о задаче: {task}")
    except Task.DoesNotExist:
        print(f"[Celery] Задача {name} не найдена")

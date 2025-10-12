"""
Документация:
https://docs.djangoproject.com/en/4.2/ref/signals/
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Task
from .tasks import send_task_reminder


@receiver(post_save, sender=Task)
def schedule_task_reminder(
    sender,
    instance,
    created,
    **kwargs,
):
    """Настройка времени до уведомления."""

    if created:
        countdown = (instance.end_date - timezone.now()).days * 86400
        if countdown > 0:
            send_task_reminder.apply_async(
                (instance.name,),
                countdown=countdown,
            )

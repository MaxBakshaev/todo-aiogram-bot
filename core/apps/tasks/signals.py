"""
Документация:
https://docs.djangoproject.com/en/4.2/ref/signals/
"""

from django.utils import timezone
from datetime import timezone as datetime_timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from celery.result import AsyncResult
from django.core.cache import cache

from .models import Task
from .tasks import send_task_reminder
from .constants import (
    LOG_SIGNALS_NO_TELEGRAM_USER,
    LOG_SIGNALS_DEADLINE_PASSED,
    LOG_SIGNALS_NOTIFICATION_SCHEDULED,
    LOG_SIGNALS_NOTIFICATION_RESCHEDULED,
    LOG_SIGNALS_TASK_REVOKED,
)


def get_reminder_task_id(task_pk: int) -> str | None:
    """
    Получает ID запланированной задачи Celery из кэша.
    """
    return cache.get(f"reminder_task_{task_pk}")


def set_reminder_task_id(task_pk: int, task_id: str) -> None:
    """
    Сохраняет ID задачи Celery в кэш.
    """
    cache.set(
        f"reminder_task_{task_pk}",
        task_id,
        timeout=None,
    )


def delete_reminder_task_id(task_pk: int) -> None:
    """
    Удаляет ID задачи Celery из кэша.
    """
    cache.delete(f"reminder_task_{task_pk}")


def cancel_existing_reminder(
    task_pk: int,
    task_name: str,
) -> bool:
    """
    Отменяет существующую запланированную задачу Celery.
    Возвращает True если задача была отменена,
    False если не было задачи или ошибка.
    """
    existing_task_id = get_reminder_task_id(task_pk)
    if not existing_task_id:
        return False

    try:
        existing_task = AsyncResult(existing_task_id)
        if not existing_task.ready():
            existing_task.revoke(terminate=True)
            print(LOG_SIGNALS_TASK_REVOKED.format(task_name))
            return True
    except Exception as e:
        print(f"Ошибка при отмене задачи {existing_task_id}: {e}")

    return False


@receiver(post_save, sender=Task)
def schedule_task_reminder(
    sender,
    instance: Task,
    created,
    **kwargs,
):
    """Планирует и перепланирует напоминания."""

    # Проверка, что пользователь связан с Telegram
    if not instance.user or not getattr(
        instance.user,
        "username",
        "",
    ).startswith("tg_"):
        print(LOG_SIGNALS_NO_TELEGRAM_USER.format(instance.name))
        return

    now = timezone.now()

    if instance.end_date > now and instance.reminder_sent_at is not None:
        Task.objects.filter(pk=instance.pk).update(reminder_sent_at=None)

    # Проверка, что дедлайн в будущем
    if instance.end_date <= now:
        print(LOG_SIGNALS_DEADLINE_PASSED.format(instance.name))

        # Отмена существующей задачи если есть
        cancel_existing_reminder(instance.pk, instance.name)
        delete_reminder_task_id(instance.pk)
        return

    # Конвертация в UTC для Celery
    eta_utc = instance.end_date.astimezone(datetime_timezone.utc)

    if created:
        # Новая задача - отменяет старую задачу и планирует новую
        cancel_existing_reminder(
            instance.pk,
            instance.name,
        )

        result = send_task_reminder.apply_async(
            args=(instance.pk,),
            eta=eta_utc,
        )

        set_reminder_task_id(
            instance.pk,
            result.id,
        )

        print(
            LOG_SIGNALS_NOTIFICATION_SCHEDULED.format(
                instance.name,
                eta_utc.isoformat(),
            )
        )

    else:
        # Отмена существующей задачи
        was_cancelled = cancel_existing_reminder(
            instance.pk,
            instance.name,
        )

        # Планирование нового напоминания
        result = send_task_reminder.apply_async(
            args=(instance.pk,),
            eta=eta_utc,
        )

        set_reminder_task_id(
            instance.pk,
            result.id,
        )

        if was_cancelled:
            print(
                LOG_SIGNALS_NOTIFICATION_RESCHEDULED.format(
                    instance.name,
                    eta_utc.isoformat(),
                )
            )
        else:
            print(
                LOG_SIGNALS_NOTIFICATION_SCHEDULED.format(
                    instance.name,
                    eta_utc.isoformat(),
                )
            )


@receiver(post_save, sender=Task)
def cleanup_past_reminders(
    sender,
    instance: Task,
    created,
    **kwargs,
):
    """Очистка данных о напоминаниях для задач с прошедшим дедлайном."""

    if created:
        return

    now = timezone.now()

    # Проверка стала ли дата завершения в прошлом
    if instance.end_date <= now:
        cancel_existing_reminder(
            instance.pk,
            instance.name,
        )
        delete_reminder_task_id(instance.pk)

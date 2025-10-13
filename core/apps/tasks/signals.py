"""
Документация:
https://docs.djangoproject.com/en/4.2/ref/signals/
"""

from django.utils import timezone
from datetime import timezone as datetime_timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Task
from .tasks import send_task_reminder


@receiver(post_save, sender=Task)
def schedule_task_reminder(
    sender,
    instance: Task,
    created,
    **kwargs,
):
    """
    АВТОМАТИЧЕСКИ ПЛАНИРУЕТ ОТПРАВКУ НАПОМИНАНИЯ ПРИ СОЗДАНИИ ЗАДАЧИ
    
    Что делает:
    1. Срабатывает каждый раз при сохранении задачи
    2. Проверяет - это новая задача? (не обновление)
    3. Проверяет - есть ли связанный Telegram пользователь?
    4. Проверяет - дедлайн в будущем?
    5. Планирует выполнение задачи send_task_reminder на время дедлайна

    Пример:
    Создана задача с дедлайном "2025-10-15 08:00"
    → Функция планирует выполнение send_task_reminder на это время
    """

    if not created:
        return

    # Проверка, что пользователь связан с Telegram
    if not instance.user or not getattr(
        instance.user,
        "username",
        "",
    ).startswith("tg_"):
        print(
            f"[signals] У задачи '{instance.name}' нет связанного Telegram пользователя"
        )
        return

    # Проверка, что дедлайн в будущем
    now = timezone.now()
    if instance.end_date <= now:
        print(
            f"[signals] Дедлайн задачи '{instance.name}' уже прошел, уведомление не планируется"
        )
        return

    # Конвертация в UTC для Celery
    eta_utc = instance.end_date.astimezone(
        datetime_timezone.utc,
    )

    # Планирование задачи
    send_task_reminder.apply_async(
        args=(instance.pk,),
        eta=eta_utc,
    )

    print(
        f"[signals] Уведомление запланировано для задачи '{instance.name}' на {eta_utc.isoformat()}"
    )

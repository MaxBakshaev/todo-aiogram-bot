"""
Документация:
https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html
"""

from celery import shared_task
from django.utils import timezone
import requests

from .models import Task
from .constants import (
    TELEGRAM_API_URL,
    LOG_CELERY_TASK_NOT_FOUND,
    LOG_CELERY_NO_TELEGRAM_USER,
    LOG_CELERY_INVALID_USERNAME_FORMAT,
    LOG_CELERY_MESSAGE_SENT,
    LOG_CELERY_TELEGRAM_API_ERROR,
    LOG_CELERY_SEND_ERROR,
    LOG_CELERY_MISSING_CREDENTIALS,
    REMINDER_MESSAGE_TEMPLATE,
    EMPTY_DESCRIPTION,
    EMPTY_CATEGORY,
    RUSSIAN_MONTHS,
)


def send_tg_message(chat_id: int, text: str) -> None:
    """
    ОТПРАВЛЯЕТ СООБЩЕНИЕ В TELEGRAM ЧЕРЕЗ BOT API

    Что делает:
    1. Проверяет наличие токена бота и ID чата
    2. Отправляет POST-запрос к Telegram API
    3. Обрабатывает возможные ошибки
    4. Логирует результат отправки

    Параметры:
    - chat_id: ID пользователя в Telegram (123456789)
    - text: Текст сообщения для отправки

    Пример вызова:
    send_tg_message(123456789, "⏰ Напоминание о задаче!")
    """

    from .constants import BOT_TOKEN

    if not BOT_TOKEN or not chat_id:
        print(
            LOG_CELERY_MISSING_CREDENTIALS.format(
                bool(BOT_TOKEN),
                chat_id,
            )
        )
        return

    try:
        response = requests.post(
            TELEGRAM_API_URL,
            json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML",
            },
            timeout=10,
        )
        if response.status_code != 200:
            print(
                LOG_CELERY_TELEGRAM_API_ERROR.format(
                    response.status_code,
                    response.text,
                )
            )
        else:
            print(LOG_CELERY_MESSAGE_SENT.format(chat_id))
    except Exception as e:
        print(LOG_CELERY_SEND_ERROR.format(e))


def format_russian_datetime(dt):
    """Форматирование даты в русский формат."""

    hour = dt.hour
    minute = f"{dt.minute:02d}"

    return f"{hour}:{minute}, {dt.day} {RUSSIAN_MONTHS[dt.month-1]} {dt.year}"


@shared_task
def send_task_reminder(task_pk):
    """
    ОТПРАВЛЯЕТ НАПОМИНАНИЕ В TELEGRAM О ЗАДАЧЕ

    Что делает:
    1. Находит задачу в базе данных по primary key
    2. Извлекает Telegram ID пользователя из username (формат: tg_123456)
    3. Форматирует дату выполнения в русском формате
    4. Отправляет сообщение в Telegram пользователю

    Пример сообщения:
    ⏰ Напоминание о задаче

    📌 Купить молоко
    📃 Не меньше 3,2%
    🔥 Срок выполнения: 8:00, 15 октября 2025
    🔖 Категория: Покупки
    """

    try:
        task = Task.objects.select_related("user").get(pk=task_pk)
    except Task.DoesNotExist:
        print(LOG_CELERY_TASK_NOT_FOUND.format(task_pk))
        return

    # Извлечение telegram_id из username пользователя (формат: tg_123456)
    if not task.user or not task.user.username.startswith("tg_"):
        print(LOG_CELERY_NO_TELEGRAM_USER.format(task.name))
        return

    try:
        telegram_id = int(task.user.username.replace("tg_", ""))
    except (ValueError, AttributeError):
        print(LOG_CELERY_INVALID_USERNAME_FORMAT.format(task.user.username))
        return

    # Конвертация времени в часовой зоне Москвы для отображения
    moscow_tz = timezone.get_current_timezone()  # Теперь будет Europe/Moscow
    local_dt = timezone.localtime(task.end_date, moscow_tz)

    # Формирование сообщения
    description = task.description or EMPTY_DESCRIPTION
    category_name = task.category.name if task.category else EMPTY_CATEGORY
    formatted_date = format_russian_datetime(local_dt)

    # Напоминание о задаче
    message = REMINDER_MESSAGE_TEMPLATE.format(
        task.name, description, formatted_date, category_name
    )

    send_tg_message(telegram_id, message)

"""
Документация:
https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html
"""

from celery import shared_task
from django.utils import timezone
import requests
import os

from .models import Task


BOT_TOKEN = os.getenv("TOKEN")


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

    if not BOT_TOKEN or not chat_id:
        print(
            f"[Celery] Не могу отправить сообщение: "
            f"BOT_TOKEN={bool(BOT_TOKEN)}, chat_id={chat_id}"
        )
        return

    try:
        response = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML",
            },
            timeout=10,
        )
        if response.status_code != 200:
            print(
                f"[Celery] Ошибка Telegram API: "
                f"{response.status_code} - {response.text}"
            )
        else:
            print(f"[Celery] Сообщение отправлено пользователю {chat_id}")
    except Exception as e:
        print(f"[Celery] Ошибка отправки TG: {e}")


def format_russian_datetime(dt):
    """Форматирование даты в русский формат."""

    months = [
        "января",
        "февраля",
        "марта",
        "апреля",
        "мая",
        "июня",
        "июля",
        "августа",
        "сентября",
        "октября",
        "ноября",
        "декабря",
    ]

    hour = dt.hour
    minute = f"{dt.minute:02d}"

    return f"{hour}:{minute}, {dt.day} {months[dt.month-1]} {dt.year}"


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
        print(f"[Celery] Задача с PK={task_pk} не найдена")
        return

    # Извлечение telegram_id из username пользователя (формат: tg_123456)
    if not task.user or not task.user.username.startswith("tg_"):
        print(
            f"[Celery] У задачи "
            f"'{task.name}' нет связанного Telegram пользователя"
        )
        return

    try:
        telegram_id = int(task.user.username.replace("tg_", ""))
    except (ValueError, AttributeError):
        print(
            f"[Celery] Неверный формат username у пользователя: "
            f"{task.user.username}"
        )
        return

    # Конвертация времени в часовой зоне America/Adak для отображения
    adak_tz = timezone.get_current_timezone()
    local_dt = timezone.localtime(task.end_date, adak_tz)

    # Напоминание о задаче
    message = (
        f"⏰ <b>Напоминание о задаче</b>\n\n"
        f"📌 <b>{task.name}</b>\n\n"
        f"📃 {task.description or 'Без описания'}\n\n"
        f"🔥 Срок выполнения:\n"
        f"<b>{format_russian_datetime(local_dt)}</b>\n\n"
        f"🔖 Категория: {task.category.name if task.category else 'Не указана'}"
    )

    send_tg_message(telegram_id, message)

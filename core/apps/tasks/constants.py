import os

# Телеграм
BOT_TOKEN = os.getenv("TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# Логи
LOG_CELERY_TASK_NOT_FOUND = "[Celery] Задача с PK={} не найдена"
LOG_CELERY_NO_TELEGRAM_USER = (
    "[Celery] У задачи '{}' нет связанного Telegram пользователя"
)
LOG_CELERY_INVALID_USERNAME_FORMAT = (
    "[Celery] Неверный формат username у пользователя: {}"
)
LOG_CELERY_MESSAGE_SENT = "[Celery] Сообщение отправлено пользователю {}"
LOG_CELERY_TELEGRAM_API_ERROR = "[Celery] Ошибка Telegram API: {} - {}"
LOG_CELERY_SEND_ERROR = "[Celery] Ошибка отправки TG: {}"
LOG_CELERY_MISSING_CREDENTIALS = (
    "[Celery] Не могу отправить сообщение: BOT_TOKEN={}, chat_id={}"
)

LOG_SIGNALS_NO_TELEGRAM_USER = (
    "[signals] У задачи '{}' нет связанного Telegram пользователя"
)
LOG_SIGNALS_DEADLINE_PASSED = (
    "[signals] Дедлайн задачи '{}' уже прошел, уведомление не планируется"
)
LOG_SIGNALS_NOTIFICATION_SCHEDULED = (
    "[signals] Уведомление запланировано для задачи '{}' на {}"
)

# Напоминание о задаче
REMINDER_MESSAGE_TEMPLATE = (
    "⏰ <b>Напоминание о задаче</b>\n\n"
    "📌 <b>{}</b>\n"
    "📃 {}\n"
    "🔥 Срок выполнения: <b>{}</b>\n"
    "🔖 Категория: {}"
)

EMPTY_DESCRIPTION = "Без описания"
EMPTY_CATEGORY = "Не указана"

# Месяцы на русском языке
RUSSIAN_MONTHS = [
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

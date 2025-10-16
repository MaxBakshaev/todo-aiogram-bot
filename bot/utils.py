"""
Документация:
- requests: https://docs.python-requests.org/
- aiohttp: https://docs.aiohttp.org/
- zoneinfo: https://docs.python.org/3/library/zoneinfo.html
"""

from aiogram.types import Message
import aiohttp
from datetime import datetime
from functools import wraps
import requests
from typing import Any
from zoneinfo import ZoneInfo

from config import (
    CATEGORIES_URL,
    SKIP_KEYWORDS,
    TASKS_URL,
    TIMEZONE,
    RU_MONTHS_GEN,
)
from messages import (
    EMPTY_FIELD,
    EMPTY_DESCRIPTION,
    ERROR_FETCH_TASKS,
    SUCCESS_NO_TASKS,
)


def tasks_check(func):
    """
    Декоратор для проверки наличия задач у пользователя.
    Автоматически обрабатывает ошибки и пустые списки.
    """

    @wraps(func)
    async def wrapper(
        message: Message,
        *args,
        **kwargs,
    ) -> Any | None:
        result = fetch_user_tasks(message.from_user.id)

        if result["error"]:
            await message.answer(
                ERROR_FETCH_TASKS.format(error=result["error"])
            )  # noqa: E501
            return

        tasks = result["tasks"]
        if not tasks:
            await message.answer(SUCCESS_NO_TASKS)
            return

        # Передача задачи в декорируемую функцию
        return await func(message, tasks, *args, **kwargs)

    return wrapper


async def find_or_create_category_id(name: str | None) -> int | None:
    """Находит ID категории по имени или создает новую категорию."""

    if not name or name.strip().lower() in SKIP_KEYWORDS:
        return None

    name = name.strip()

    try:
        # Поиск существующей категории
        response = requests.get(
            CATEGORIES_URL,
            params={"name": name},
            timeout=10,
        )
        if response.status_code == 200:
            data = response.json()
            items = data.get("results", []) if isinstance(data, dict) else data

            for item in items:
                if isinstance(item, dict) and item.get("name") == name:
                    return item.get("id")
    except Exception:
        pass

    # Создание новой категории
    async with aiohttp.ClientSession() as session:
        async with session.post(
            CATEGORIES_URL, json={"name": name}, timeout=10
        ) as response:
            if response.status in (200, 201):
                created = await response.json()
                return created.get("id")

    return None


def format_readable(iso_dt: str) -> str:
    """Преобразует ISO-дату в читаемый формат с учетом часового пояса."""

    if not iso_dt:
        return EMPTY_FIELD
    try:
        if iso_dt.endswith("Z"):
            iso_dt = iso_dt.replace("Z", "+00:00")

        dt = datetime.fromisoformat(iso_dt)
        moscow_tz = ZoneInfo(TIMEZONE)
        dt = dt.astimezone(moscow_tz)

        hhmm = f"{dt.hour}:{dt.minute:02d}"
        return f"{hhmm}, {dt.day} {RU_MONTHS_GEN[dt.month]} {dt.year}"
    except Exception:
        return iso_dt


def format_single_task(task: dict) -> str:
    """
    Форматирует данные одной задачи в читаемую строку.

    Пример возврата:
    '''
    📌 Задача: Купить молоко
    📃 Описание: Не меньше 3,2%
    🔖 Категория: Покупки
    🕒 Дата создания: 8:00, 15 октября 2025
    🔥 Дата завершения: 9:00, 16 октября 2025
    '''
    """

    from messages import TASK_FORMAT

    name = task.get("name", EMPTY_FIELD)
    description = task.get("description") or EMPTY_DESCRIPTION
    category_data = task.get("category") or {}
    category_name = (
        category_data.get("name")
        if isinstance(category_data, dict)
        else EMPTY_FIELD  # noqa: E501
    )
    created_date = format_readable(task.get("creation_date"))
    end_date = format_readable(task.get("end_date"))

    return TASK_FORMAT.format(
        name=name,
        description=description,
        category=category_name,
        created_date=created_date,
        end_date=end_date,
    )


def fetch_user_tasks(user_telegram_id: int) -> dict[str, Any]:
    """
    Получает список задач пользователя из Django API.

    Возвращает словарь с ключами:
    - "error": str | None - описание ошибки или None если успешно
    - "tasks": list - список задач пользователя
    """

    try:
        response = requests.get(
            TASKS_URL,
            params={"user_telegram_id": user_telegram_id},
            timeout=10,
        )
    except requests.RequestException as e:
        return {"error": str(e), "tasks": []}

    if response.status_code != 200:
        return {
            "error": f"HTTP {response.status_code}: {response.text}",
            "tasks": [],
        }

    data = response.json()
    if isinstance(data, dict) and isinstance(data.get("results"), list):
        tasks = data["results"]
    elif isinstance(data, list):
        tasks = data
    else:
        tasks = []
    return {"error": None, "tasks": tasks}


def fetch_single_task(
    task_id: str,
    user_telegram_id: int,
) -> dict[str, Any]:
    """Получает конкретную задачу по ID."""

    try:
        response = requests.get(
            f"{TASKS_URL}{task_id}/",
            params={"user_telegram_id": user_telegram_id},
            timeout=10,
        )
    except requests.RequestException as e:
        return {"error": str(e), "task": None}

    if response.status_code != 200:
        return {
            "error": f"HTTP {response.status_code}: {response.text}",
            "task": None,
        }

    return {"error": None, "task": response.json()}


async def update_task(
    task_id: str,
    update_data: dict,
    user_telegram_id: int,
) -> dict[str, Any]:
    """Обновляет задачу через API."""

    try:
        async with aiohttp.ClientSession() as session:
            async with session.patch(
                f"{TASKS_URL}{task_id}/",
                json=update_data,
                params={"user_telegram_id": user_telegram_id},
                timeout=10,
            ) as response:
                if response.status == 200:
                    return {"error": None, "task": await response.json()}
                else:
                    error_text = await response.text()
                    return {
                        "error": f"HTTP {response.status}: {error_text}",
                        "task": None,
                    }
    except Exception as e:
        return {"error": str(e), "task": None}


async def delete_task(
    task_id: str,
    user_telegram_id: int,
) -> dict[str, Any]:
    """Удаляет задачу через API."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                f"{TASKS_URL}{task_id}/",
                params={"user_telegram_id": user_telegram_id},
                timeout=10,
            ) as response:
                if response.status in (200, 204):
                    return {"error": None}
                else:
                    error_text = await response.text()
                    return {"error": f"HTTP {response.status}: {error_text}"}
    except Exception as e:
        return {"error": str(e)}


def format_task_for_list(task: dict, index: int) -> str:
    """Форматирует задачу для отображения в списке с номером."""

    task_text = format_single_task(task)
    return f"#{index + 1}\n{task_text}"

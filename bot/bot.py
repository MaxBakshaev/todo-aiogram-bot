import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo

from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command

import aiohttp
import requests

import os
import sys

# fmt: off
from config import (
    TASKS_URL, CATEGORIES_URL, BOT_TOKEN, TIMEZONE,
    DATE_INPUT_FORMAT, SKIP_KEYWORDS, RU_MONTHS_GEN,
)
from messages import (
    START_MESSAGE, ADD_TASK_NAME, ADD_TASK_DESCRIPTION, ADD_TASK_CATEGORY,
    ADD_TASK_END_DATE, ERROR_DATE_FORMAT, ERROR_FETCH_TASKS,
    ERROR_CREATE_TASK, ERROR_CONNECTION, ERROR_READ_RESPONSE,
    SUCCESS_TASK_CREATED, SUCCESS_NO_TASKS, TASK_LIST_HEADER,
    TASK_FORMAT, EMPTY_FIELD, EMPTY_DESCRIPTION,
)
# fmt: on

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

user_task_data: dict[int, dict] = {}


def format_readable(iso_dt: str) -> str:
    """
    ПРЕОБРАЗУЕТ ISO-ДАТУ В ЧИТАЕМЫЙ ФОРМАТ

    1. Принимает дату в формате "2025-10-13T10:00:00Z"
    2. Конвертирует в часовой пояс America/Adak
    3. Форматирует как "8:00, 15 октября 2025"

    Пример:
    Вход: "2025-10-13T10:00:00Z"
    Выход: "8:00, 15 октября 2025"
    """

    if not iso_dt:
        return EMPTY_FIELD
    try:
        if iso_dt.endswith("Z"):
            iso_dt = iso_dt.replace("Z", "+00:00")

        dt = datetime.fromisoformat(iso_dt)
        adak = ZoneInfo(TIMEZONE)
        dt = dt.astimezone(adak)

        hhmm = f"{dt.hour}:{dt.minute:02d}"
        return f"{hhmm}, {dt.day} {RU_MONTHS_GEN[dt.month]} {dt.year}"
    except Exception:
        return iso_dt


def fetch_user_tasks(user_telegram_id: int):
    """
    ПОЛУЧАЕТ СПИСОК ЗАДАЧ ПОЛЬЗОВАТЕЛЯ ИЗ DJANGO API

    1. Отправляет GET-запрос с параметром user_telegram_id
    2. Обрабатывает возможные ошибки сети
    3. Парсит JSON-ответ
    4. Возвращает словарь с задачами или ошибкой

    Пример возврата:
    {
        "error": None,
        "tasks": [
            {"name": "Задача 1", "description": "...", ...},
            {"name": "Задача 2", "description": "...", ...}
        ]
    }
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


async def find_or_create_category_id(name: str | None) -> int | None:
    """Находит или создает категорию по имени."""

    if not name or name.strip().lower() in SKIP_KEYWORDS:
        return None

    name = name.strip()

    try:
        # Фильтрация по имени
        response = requests.get(
            CATEGORIES_URL,
            params={"name": name},
            timeout=10,
        )
        if response.status_code == 200:
            data = response.json()

            # Обработка обоих форматов ответа
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


async def create_task_in_django(task_data: dict) -> aiohttp.ClientResponse:
    """
    ОТПРАВЛЯЕТ POST-ЗАПРОС НА DJANGO API ДЛЯ СОЗДАНИЯ ЗАДАЧИ

    1. Создает асинхронную HTTP-сессию
    2. Отправляет JSON с данными задачи на endpoint /api/tasks/
    3. Возвращает ответ от сервера

    Пример task_data:
    {
        "name": "Купить молоко",
        "description": "Не меньше 3,2%",
        "end_date": "2025-10-15T08:00:00-10:00",
        "user_telegram_id": 123456789,
        "category_id": "2025-10-15T08:00:00-10:00"
    }
    """

    async with aiohttp.ClientSession() as session:
        async with session.post(
            TASKS_URL,
            json=task_data,
            timeout=10,
        ) as response:
            return response


@dp.message(Command("start"))
async def start(message: Message) -> None:
    await message.answer(START_MESSAGE)


@dp.message(Command("add_task"))
async def add_task(message: types.Message) -> None:
    """Начало процесса добавления задачи."""

    user_id = message.from_user.id
    user_task_data[user_id] = {}
    await message.answer(ADD_TASK_NAME)


@dp.message(
    lambda m: m.from_user.id in user_task_data
    and "name" not in user_task_data[m.from_user.id]
)
async def task_name(message: types.Message) -> None:
    """Обработчик названия задачи."""

    user_task_data[message.from_user.id]["name"] = message.text.strip()
    await message.answer(ADD_TASK_DESCRIPTION)


@dp.message(
    lambda m: m.from_user.id in user_task_data
    and "description" not in user_task_data[m.from_user.id]
)
async def task_description(message: types.Message) -> None:
    """Обработчик описания задачи."""

    user_task_data[message.from_user.id]["description"] = message.text.strip()
    await message.answer(ADD_TASK_CATEGORY)


@dp.message(
    lambda m: m.from_user.id in user_task_data
    and "category_name" not in user_task_data[m.from_user.id]
)
async def task_category(message: types.Message) -> None:
    """Обработчик категории задачи."""

    user_task_data[message.from_user.id][
        "category_name"
    ] = message.text.strip()  # noqa: E501
    await message.answer(ADD_TASK_END_DATE)


@dp.message(
    lambda m: m.from_user.id in user_task_data
    and "end_date" not in user_task_data[m.from_user.id]
)
async def task_end_date(message: types.Message) -> None:
    """
    ОБРАБОТЧИК СООБЩЕНИЯ С ДАТОЙ ЗАВЕРШЕНИЯ ЗАДАЧИ

    1. Принимает дату от пользователя в формате "YYYY-MM-DD HH:mm"
    2. Парсит и конвертирует в часовой пояс America/Adak
    3. Собирает все данные задачи в один словарь
    4. Отправляет запрос на создание задачи в Django API
    5. Уведомляет пользователя о результате

    Пример диалога:
    Пользователь: "2025-10-15 14:30"
    Бот: "Задача «Купить молоко» успешно создана!"
    """

    user_id = message.from_user.id
    try:
        adak = ZoneInfo(TIMEZONE)
        end_dt = datetime.strptime(
            message.text.strip(),
            DATE_INPUT_FORMAT,
        ).replace(tzinfo=adak)
        user_task_data[user_id]["end_date"] = end_dt.isoformat()
    except ValueError:
        await message.answer(ERROR_DATE_FORMAT)
        return

    category_name = user_task_data[user_id].get("category_name")
    category_id = await find_or_create_category_id(category_name)

    # Формирование данных для отправки в API
    task_payload = {
        "name": user_task_data[user_id]["name"],
        "description": user_task_data[user_id]["description"],
        "end_date": user_task_data[user_id]["end_date"],
        "user_telegram_id": message.from_user.id,
    }
    if category_id:
        task_payload["category_id"] = category_id

    try:
        # Отправленние запроса на создание задачи
        response = await create_task_in_django(task_payload)

        if response.status in (200, 201):
            task_name = user_task_data[user_id]["name"]
            await message.answer(
                SUCCESS_TASK_CREATED.format(task_name=task_name),
            )
        else:
            try:
                error_text = await response.text()
                await message.answer(
                    ERROR_CREATE_TASK.format(
                        status=response.status,
                        details=error_text[:200],
                    )
                )
            except Exception:
                await message.answer(
                    ERROR_CREATE_TASK.format(
                        status=response.status,
                        details=ERROR_READ_RESPONSE,
                    )
                )

    except Exception as e:
        await message.answer(ERROR_CONNECTION.format(error=str(e)))

    finally:
        # Очистка временных данных пользователя
        user_task_data.pop(user_id, None)


@dp.message(Command("tasks"))
async def list_tasks(message: types.Message) -> None:
    """
    ПОКАЗЫВАЕТ ПОЛЬЗОВАТЕЛЮ ВСЕ ЕГО ЗАДАЧИ

    Что делает:
    1. Получает задачи пользователя из Django API
    2. Форматирует каждую задачу в читаемый вид
    3. Объединяет все задачи в один большой текст
    4. Отправляет пользователю форматированный список

    Пример вывода:
    Ваши задачи:

    📌 Задача: Купить молоко
    📃 Описание: Не забыть вечером
    🔖 Категория: Покупки
    🕒 Дата создания: 8:00, 13 октября 2025
    🔥 Дата завершения: 8:00, 15 октября 2025

    📌 Задача: Сделать ДЗ
    📃 Описание: Математика и физика
    🔖 Категория: Учеба
    🕒 Дата создания: 9:00, 13 октября 2025
    🔥 Дата завершения: 10:00, 16 октября 2025
    """

    result = fetch_user_tasks(message.from_user.id)
    if result["error"]:
        await message.answer(ERROR_FETCH_TASKS.format(error=result["error"]))
        return

    tasks = result["tasks"]
    if not tasks:
        await message.answer(SUCCESS_NO_TASKS)
        return

    def format_single_task(task: dict) -> str:
        """Форматирование одной задачи."""

        name = task.get("name", EMPTY_FIELD)
        description = task.get("description") or EMPTY_DESCRIPTION
        category_data = task.get("category") or {}
        category_name = (
            category_data.get("name")
            if isinstance(category_data, dict)
            else EMPTY_FIELD
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

    # Форматирование и объединение всех задач
    task_list = "\n\n".join(
        format_single_task(task) for task in tasks if isinstance(task, dict)
    )
    await message.answer(TASK_LIST_HEADER + task_list)


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

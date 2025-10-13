import os
import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo

from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command

import aiohttp
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL")
TASKS_URL = f"{API_URL}/tasks/"
CATEGORIES_URL = f"{API_URL}/categories/"

BOT_TOKEN = os.getenv("TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

user_task_data: dict[int, dict] = {}

RU_MONTHS_GEN = {
    1: "января",
    2: "февраля",
    3: "марта",
    4: "апреля",
    5: "мая",
    6: "июня",
    7: "июля",
    8: "августа",
    9: "сентября",
    10: "октября",
    11: "ноября",
    12: "декабря",
}


def fmt_human(iso_dt: str) -> str:
    """
    ПРЕОБРАЗУЕТ ISO-ДАТУ В ЧЕЛОВЕКО-ЧИТАЕМЫЙ РУССКИЙ ФОРМАТ
    
    Что делает:
    1. Принимает дату в формате "2025-10-15T08:00:00-10:00"
    2. Конвертирует в часовой пояс America/Adak
    3. Форматирует как "8:00, 15 октября 2025"

    Пример:
    Вход: "2025-10-15T08:00:00-10:00"
    Выход: "8:00, 15 октября 2025"
    """

    if not iso_dt:
        return "—"
    try:
        if iso_dt.endswith("Z"):
            iso_dt = iso_dt.replace("Z", "+00:00")
        dt = datetime.fromisoformat(iso_dt)
        adak = ZoneInfo("America/Adak")
        dt = dt.astimezone(adak)

        hhmm = f"{dt.hour}:{dt.minute:02d}"
        return f"{hhmm}, {dt.day} {RU_MONTHS_GEN[dt.month]} {dt.year}"
    except Exception:
        return iso_dt


def fetch_user_tasks(user_telegram_id: int):
    """
    ПОЛУЧАЕТ СПИСОК ЗАДАЧ ПОЛЬЗОВАТЕЛЯ ИЗ DJANGO API

    Что делает:
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
        resp = requests.get(
            TASKS_URL,
            params={"user_telegram_id": user_telegram_id},
            timeout=10,
        )
    except requests.RequestException as e:
        return {"error": str(e), "tasks": []}

    if resp.status_code != 200:
        return {"error": f"HTTP {resp.status_code}: {resp.text}", "tasks": []}

    data = resp.json()
    if isinstance(data, dict) and isinstance(data.get("results"), list):
        tasks = data["results"]
    elif isinstance(data, list):
        tasks = data
    else:
        tasks = []
    return {"error": None, "tasks": tasks}


async def find_or_create_category_id(name: str | None) -> int | None:
    """
    НАХОДИТ ИЛИ СОЗДАЕТ КАТЕГОРИЮ ПО ИМЕНИ
    
    Что делает:
    1. Если имя пустое или "пропустить" - возвращает None
    2. Ищет категорию в базе через API
    3. Если не находит - создает новую категорию
    4. Возвращает ID категории (primary key)

    Пример:
    Вход: "Работа" → Выход: "2025-10-15T08:00:00-10:00"
    Вход: "пропустить" → Выход: None
    """
    if not name or name.strip().lower() in {
        "-",
        "—",
        "пропустить",
        "skip",
        "none",
        "null",
    }:
        return None
    name = name.strip()

    try:
        r = requests.get(
            CATEGORIES_URL,
            params={"name": name},
            timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            items = (
                data["results"]
                if isinstance(data, dict) and "results" in data
                else data
            )
            for it in items or []:
                if isinstance(it, dict) and it.get("name") == name:
                    return it.get("id") or it.get("creation_date")
    except Exception:
        pass

    async with aiohttp.ClientSession() as session:
        async with session.post(
            CATEGORIES_URL, json={"name": name}, timeout=10
        ) as resp:
            if resp.status in (200, 201):
                created = await resp.json()
                return created.get("id") or created.get("creation_date")

            if resp.status == 400:
                r2 = requests.get(
                    CATEGORIES_URL,
                    params={"name": name},
                    timeout=10,
                )
                if r2.status_code == 200:
                    data = r2.json()
                    items = (
                        data["results"]
                        if isinstance(data, dict) and "results" in data
                        else data
                    )
                    for it in items or []:
                        if isinstance(it, dict) and it.get("name") == name:
                            return it.get("id") or it.get("creation_date")
    return None


async def create_task_in_django(task_data: dict) -> aiohttp.ClientResponse:
    """
    ОТПРАВЛЯЕТ POST-ЗАПРОС НА DJANGO API ДЛЯ СОЗДАНИЯ ЗАДАЧИ
    
    Что делает:
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
async def start(message: Message):
    await message.answer("Привет! Команды: /add_task и /tasks")


@dp.message(Command("add_task"))
async def add_task(message: types.Message):
    uid = message.from_user.id
    user_task_data[uid] = {}
    await message.answer("Отправь название задачи:")


@dp.message(
    lambda m: m.from_user.id in user_task_data
    and "name" not in user_task_data[m.from_user.id]
)
async def task_name(message: types.Message):
    user_task_data[message.from_user.id]["name"] = message.text.strip()
    await message.answer("Отправь описание задачи:")


@dp.message(
    lambda m: m.from_user.id in user_task_data
    and "description" not in user_task_data[m.from_user.id]
)
async def task_description(message: types.Message):
    user_task_data[message.from_user.id]["description"] = message.text.strip()
    await message.answer("Укажи категорию (или напиши «пропустить»):")


@dp.message(
    lambda m: m.from_user.id in user_task_data
    and "category_name" not in user_task_data[m.from_user.id]
)
async def task_category(message: types.Message):
    user_task_data[message.from_user.id]["category_name"] = message.text.strip()
    await message.answer(
        "Отправь дату завершения в формате YYYY-MM-DD HH:mm (America/Adak):"
    )


@dp.message(
    lambda m: m.from_user.id in user_task_data
    and "end_date" not in user_task_data[m.from_user.id]
)
async def task_end_date(message: types.Message):
    """
    ОБРАБОТЧИК СООБЩЕНИЯ С ДАТОЙ ЗАВЕРШЕНИЯ ЗАДАЧИ

    Что делает:
    1. Принимает дату от пользователя в формате "YYYY-MM-DD HH:mm"
    2. Парсит и конвертирует в часовой пояс America/Adak
    3. Собирает все данные задачи в один словарь
    4. Отправляет запрос на создание задачи в Django API
    5. Уведомляет пользователя о результате

    Пример диалога:
    Пользователь: "2025-10-15 14:30"
    Бот: "Задача «Купить молоко» успешно создана!"
    """

    uid = message.from_user.id
    try:
        adak = ZoneInfo("America/Adak")
        end_dt = datetime.strptime(
            message.text.strip(),
            "%Y-%m-%d %H:%M",
        ).replace(tzinfo=adak)
        user_task_data[uid]["end_date"] = end_dt.isoformat()
    except ValueError:
        await message.answer(
            "Неверный формат. Нужен YYYY-MM-DD HH:mm. Попробуй ещё раз:"
        )
        return

    category_name = user_task_data[uid].get("category_name")
    category_id = await find_or_create_category_id(category_name)

    # Формирование данных для отправки в API
    task_payload = {
        "name": user_task_data[uid]["name"],
        "description": user_task_data[uid]["description"],
        "end_date": user_task_data[uid]["end_date"],
        "user_telegram_id": message.from_user.id,
    }
    if category_id:
        task_payload["category_id"] = category_id

    try:
        # Отправленние запроса на создание задачи
        response = await create_task_in_django(task_payload)

        if response.status in (200, 201):
            await message.answer(
                f"Задача «{user_task_data[uid]['name']}» успешно создана!"
            )
        else:
            try:
                error_text = await response.text()
                await message.answer(
                    f"Ошибка при создании задачи: {response.status}\n"
                    f"{error_text[:200]}"
                )
            except Exception:
                await message.answer(
                    f"Ошибка при создании задачи: {response.status}\n"
                    f"Не удалось прочитать ответ"
                )

    except Exception as e:
        await message.answer(f"Ошибка соединения с сервером: {str(e)}")

    finally:
        # Очистка временных данных пользователя
        user_task_data.pop(uid, None)


@dp.message(Command("tasks"))
async def list_tasks(message: types.Message):
    """
    ОКАЗЫВАЕТ ПОЛЬЗОВАТЕЛЮ ВСЕ ЕГО ЗАДАЧИ

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
        await message.answer(f"Не удалось получить задачи: {result['error']}")
        return

    tasks = result["tasks"]
    if not tasks:
        await message.answer("У вас нет задач.")
        return

    def fmt(task: dict) -> str:
        """Форматирование одной задачи."""

        name = task.get("name", "—")
        desc = task.get("description") or "—"
        cat = task.get("category") or {}
        cat_name = cat.get("name") if isinstance(cat, dict) else "—"
        created = fmt_human(task.get("creation_date"))
        end = fmt_human(task.get("end_date"))
        return (
            f"📌 Задача: {name}\n"
            f"📃 Описание: {desc}\n"
            f"🔖 Категория: {cat_name}\n"
            f"🕒 Дата создания: {created}\n"
            f"🔥 Дата завершения: {end}"
        )

    # Форматирование и объединение всех задач
    task_list = "\n\n".join(fmt(t) for t in tasks if isinstance(t, dict))
    await message.answer(f"Ваши задачи:\n\n{task_list}")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

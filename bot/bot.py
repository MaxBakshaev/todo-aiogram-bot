import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo

from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
from aiogram_dialog import DialogManager, StartMode, setup_dialogs

import requests

from config import TASKS_URL, TIMEZONE, RU_MONTHS_GEN, BOT_TOKEN
from messages import (
    START_MESSAGE,
    ERROR_FETCH_TASKS,
    SUCCESS_NO_TASKS,
    TASK_LIST_HEADER,
    TASK_FORMAT,
    EMPTY_FIELD,
    EMPTY_DESCRIPTION,
)
from add_task import add_task_dialog
from states import AddTaskStates

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dp.include_router(add_task_dialog)
setup_dialogs(dp)


@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(START_MESSAGE)


@dp.message(Command("add_task"))
async def add_task_command(
    message: Message,
    dialog_manager: DialogManager,
):
    await dialog_manager.start(
        AddTaskStates.name,
        mode=StartMode.RESET_STACK,
    )


@dp.message(Command("tasks"))
async def list_tasks(message: types.Message):
    result = fetch_user_tasks(message.from_user.id)

    if result["error"]:
        await message.answer(ERROR_FETCH_TASKS.format(error=result["error"]))
        return

    tasks = result["tasks"]
    if not tasks:
        await message.answer(SUCCESS_NO_TASKS)
        return

    def format_single_task(task: dict) -> str:
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

    task_list = "\n\n".join(
        format_single_task(task) for task in tasks if isinstance(task, dict)
    )
    await message.answer(TASK_LIST_HEADER + task_list)


def format_readable(iso_dt: str) -> str:
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


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

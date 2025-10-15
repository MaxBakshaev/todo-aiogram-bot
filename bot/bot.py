"""
Документация:
- Aiogram: https://docs.aiogram.dev/
- Aiogram Dialog: https://aiogram-dialog.readthedocs.io/
- Telegram Bot API: https://core.telegram.org/bots/api
"""

import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
from aiogram_dialog import DialogManager, StartMode, setup_dialogs

from config import BOT_TOKEN
from messages import (
    START_MESSAGE,
    ERROR_FETCH_TASKS,
    SUCCESS_NO_TASKS,
    TASK_LIST_HEADER,
)
from add_task import add_task_dialog
from states import AddTaskStates
from utils import fetch_user_tasks, format_single_task


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dp.include_router(add_task_dialog)
setup_dialogs(dp)


@dp.message(Command("start"))
async def start(message: Message):
    """Обработчик команды /start."""

    await message.answer(START_MESSAGE)


@dp.message(Command("add_task"))
async def add_task_command(message: Message, dialog_manager: DialogManager):
    """Запуск диалога добавления новой задачи."""

    await dialog_manager.start(AddTaskStates.name, mode=StartMode.RESET_STACK)


@dp.message(Command("tasks"))
async def list_tasks(message: types.Message):
    """Показывает список всех задач пользователя."""

    # Получение задач пользователя через API
    result = fetch_user_tasks(message.from_user.id)

    if result["error"]:
        await message.answer(ERROR_FETCH_TASKS.format(error=result["error"]))
        return

    tasks = result["tasks"]
    if not tasks:
        await message.answer(SUCCESS_NO_TASKS)
        return

    # Форматирование и отправка списка задач
    task_list = "\n\n".join(
        format_single_task(task) for task in tasks if isinstance(task, dict)
    )
    await message.answer(TASK_LIST_HEADER + task_list)


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

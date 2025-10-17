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
    TASK_LIST_HEADER,
)
from add_task import add_task_dialog
from edit_task import edit_task_dialog
from delete_task import delete_task_dialog
from states import AddTaskStates, EditTaskStates, DeleteTaskStates
from utils import format_single_task, tasks_check


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dp.include_router(add_task_dialog)
dp.include_router(edit_task_dialog)
dp.include_router(delete_task_dialog)
setup_dialogs(dp)


@dp.message(Command("start"))
async def start(message: Message):
    """Обработчик команды /start."""

    await message.answer(START_MESSAGE)


@dp.message(Command("add_task"))
async def add_task_command(
    message: Message,
    dialog_manager: DialogManager,
) -> None:
    """Запуск диалога добавления новой задачи."""

    await dialog_manager.start(
        AddTaskStates.name,
        mode=StartMode.RESET_STACK,
    )


@dp.message(Command("edit_task"))
@tasks_check
async def edit_task_command(
    message: Message,
    tasks: list,
    dialog_manager: DialogManager,
) -> None:
    """Запуск диалога редактирования задачи."""

    await dialog_manager.start(
        EditTaskStates.select_task,
        mode=StartMode.RESET_STACK,
    )


@dp.message(Command("delete_task"))
@tasks_check
async def delete_task_command(
    message: Message,
    tasks: list,
    dialog_manager: DialogManager,
) -> None:
    """Запуск диалога удаления задачи."""

    await dialog_manager.start(
        DeleteTaskStates.select_task,
        mode=StartMode.RESET_STACK,
    )


@dp.message(Command("tasks"))
@tasks_check
async def list_tasks(
    message: types.Message,
    tasks: list,
) -> None:
    """Показывает список всех задач пользователя."""

    # Форматирование списка задач
    task_list = "\n\n".join(
        format_single_task(task) for task in tasks if isinstance(task, dict)
    )

    await message.answer(TASK_LIST_HEADER + task_list)


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

from aiogram.types import Message
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.text import Const
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput
from aiogram_dialog.widgets.kbd import Button, Back, Cancel

import aiohttp
from datetime import datetime
from zoneinfo import ZoneInfo

from config import TASKS_URL, TIMEZONE
from messages import (
    TASK_NAME_PROMPT,
    TASK_DESCRIPTION_PROMPT,
    TASK_CATEGORY_PROMPT,
    TASK_END_DATE_PROMPT,
    ERROR_DATE_FORMAT,
    SUCCESS_TASK_CREATED,
    TASK_CREATION_CANCELLED,
    BUTTON_BACK,
    BUTTON_CANCEL,
)
from utils import find_or_create_category_id
from states import AddTaskStates


async def on_task_name_entered(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    text: str,
):
    dialog_manager.dialog_data["name"] = text
    await dialog_manager.next()


async def on_task_description_entered(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    text: str,
):
    dialog_manager.dialog_data["description"] = text
    await dialog_manager.next()


async def on_task_category_entered(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    text: str,
):
    if text.lower() in ["пропустить", "skip", "-", "нет"]:
        dialog_manager.dialog_data["category_name"] = None
    else:
        dialog_manager.dialog_data["category_name"] = text
    await dialog_manager.next()


async def create_task_from_dialog(dialog_manager: DialogManager):
    data = dialog_manager.dialog_data
    user_id = dialog_manager.event.from_user.id

    task_payload = {
        "name": data["name"],
        "description": data.get("description", ""),
        "end_date": data["end_date"],
        "user_telegram_id": user_id,
    }

    category_name = data.get("category_name")
    if category_name:
        category_id = await find_or_create_category_id(category_name)
        if category_id:
            task_payload["category_id"] = category_id

    async with aiohttp.ClientSession() as session:
        async with session.post(TASKS_URL, json=task_payload) as response:
            if response.status not in (200, 201):
                error_text = await response.text()
                await dialog_manager.event.answer(
                    f"❌ Ошибка при создании задачи: {error_text}"
                )


async def on_task_end_date_entered(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    text: str,
):
    try:
        adak = ZoneInfo(TIMEZONE)
        end_dt = datetime.strptime(text, "%Y-%m-%d %H:%M").replace(tzinfo=adak)
        dialog_manager.dialog_data["end_date"] = end_dt.isoformat()

        await create_task_from_dialog(dialog_manager)
        await message.answer(SUCCESS_TASK_CREATED)
        await dialog_manager.done()
    except ValueError:
        await message.answer(ERROR_DATE_FORMAT)


async def on_cancel_clicked(
    message: Message, button: Button, dialog_manager: DialogManager
):
    await message.answer(TASK_CREATION_CANCELLED)
    await dialog_manager.done()


add_task_dialog = Dialog(
    Window(
        Const(TASK_NAME_PROMPT),
        TextInput(id="task_name_input", on_success=on_task_name_entered),
        Cancel(Const(BUTTON_CANCEL), on_click=on_cancel_clicked),
        state=AddTaskStates.name,
    ),
    Window(
        Const(TASK_DESCRIPTION_PROMPT),
        TextInput(
            id="task_description_input",
            on_success=on_task_description_entered,
        ),
        Back(Const(BUTTON_BACK)),
        Cancel(Const(BUTTON_CANCEL), on_click=on_cancel_clicked),
        state=AddTaskStates.description,
    ),
    Window(
        Const(TASK_CATEGORY_PROMPT),
        TextInput(
            id="task_category_input",
            on_success=on_task_category_entered,
        ),
        Back(Const(BUTTON_BACK)),
        Cancel(Const(BUTTON_CANCEL), on_click=on_cancel_clicked),
        state=AddTaskStates.category,
    ),
    Window(
        Const(TASK_END_DATE_PROMPT.format(timezone=TIMEZONE)),
        TextInput(
            id="task_end_date_input",
            on_success=on_task_end_date_entered,
        ),
        Back(Const(BUTTON_BACK)),
        Cancel(Const(BUTTON_CANCEL), on_click=on_cancel_clicked),
        state=AddTaskStates.end_date,
    ),
)

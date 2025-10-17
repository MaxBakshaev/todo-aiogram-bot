from typing import Any
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput
from aiogram_dialog.widgets.kbd import (
    Button,
    Back,
    Cancel,
    Column,
    Group,
    Select,
)

from datetime import datetime
from zoneinfo import ZoneInfo

from config import TIMEZONE
from messages import (
    BUTTON_BACK,
    BUTTON_CANCEL,
    TASK_NAME_PROMPT,
    TASK_DESCRIPTION_PROMPT,
    TASK_CATEGORY_PROMPT,
    TASK_END_DATE_PROMPT,
    ERROR_DATE_FORMAT,
    SUCCESS_TASK_UPDATED,
    TASK_UPDATE_CANCELLED,
    ERROR_LOAD_TASK,
    ERROR_UPDATE_TASK,
    ERROR_CREATE_CATEGORY,
    SELECT_TASK_EDIT,
    EDIT_TASK_HEADER,
    BUTTON_EDIT_NAME,
    BUTTON_EDIT_DESCRIPTION,
    BUTTON_EDIT_CATEGORY,
    BUTTON_EDIT_END_DATE,
    NO_DESCRIPTION,
    NO_CATEGORY,
)
from utils import (
    fetch_user_tasks,
    update_task,
    find_or_create_category_id,
    fetch_single_task,
)
from states import EditTaskStates


async def get_tasks_for_editing(
    dialog_manager: DialogManager,
    **kwargs,
) -> dict[str, Any]:
    """Получает задачи пользователя для выбора при редактировании."""

    user_id = dialog_manager.event.from_user.id
    result = fetch_user_tasks(user_id)

    tasks = result.get("tasks", [])
    task_choices = [
        (
            f"#{i+1}: {task['name']}",
            str(task["id"]),
        )
        for i, task in enumerate(tasks)
    ]

    return {
        "tasks": tasks,
        "task_choices": task_choices,
        "has_tasks": len(tasks) > 0,
        "error": result.get("error"),
    }


async def on_task_selected_for_edit(
    callback: CallbackQuery,
    widget: Select,
    dialog_manager: DialogManager,
    item_id: str,
) -> None:
    """Обработчик выбора задачи для редактирования."""

    dialog_manager.dialog_data["task_id"] = item_id
    await dialog_manager.next()


async def get_task_data(
    dialog_manager: DialogManager,
    **kwargs,
) -> dict | dict[str, Any]:
    """Получает данные выбранной задачи."""

    task_id = dialog_manager.dialog_data.get("task_id")
    user_id = dialog_manager.event.from_user.id

    result = fetch_single_task(
        task_id,
        user_id,
    )

    if result["error"]:
        await dialog_manager.event.answer(
            ERROR_LOAD_TASK.format(error=result["error"]),
        )
        await dialog_manager.done()
        return {}

    task = result["task"]
    dialog_manager.dialog_data["current_task"] = task

    category_name = NO_CATEGORY
    if task.get("category") and isinstance(
        task["category"],
        dict,
    ):
        category_name = task["category"].get(
            "name",
            NO_CATEGORY,
        )

    return {
        "task_name": task.get("name", ""),
        "task_description": task.get(
            "description",
            "",
        )
        or NO_DESCRIPTION,
        "task_category": category_name,
    }


# Обработчики для кнопок выбора поля
async def on_name_edit_clicked(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
) -> None:
    """Обработчик кнопки редактирования названия."""

    dialog_manager.dialog_data["editing_field"] = "name"
    await dialog_manager.switch_to(EditTaskStates.edit_name)


async def on_description_edit_clicked(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
) -> None:
    """Обработчик кнопки редактирования описания."""

    dialog_manager.dialog_data["editing_field"] = "description"
    await dialog_manager.switch_to(EditTaskStates.edit_description)


async def on_category_edit_clicked(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
) -> None:
    """Обработчик кнопки редактирования категории."""

    dialog_manager.dialog_data["editing_field"] = "category"
    await dialog_manager.switch_to(EditTaskStates.edit_category)


async def on_end_date_edit_clicked(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
) -> None:
    """Обработчик кнопки редактирования даты завершения."""

    dialog_manager.dialog_data["editing_field"] = "end_date"
    await dialog_manager.switch_to(EditTaskStates.edit_end_date)


# Обработчики ввода данных
async def on_name_updated(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    text: str,
) -> None:
    """Обработчик обновления названия задачи."""

    task_id = dialog_manager.dialog_data["task_id"]
    user_id = dialog_manager.event.from_user.id

    result = await update_task(
        task_id,
        {"name": text},
        user_id,
    )

    if result["error"]:
        await message.answer(
            ERROR_UPDATE_TASK.format(
                error=result["error"],
            )
        )
    else:
        await message.answer(SUCCESS_TASK_UPDATED)

    await dialog_manager.done()


async def on_description_updated(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    text: str,
) -> None:
    """Обработчик обновления описания задачи."""

    task_id = dialog_manager.dialog_data["task_id"]
    user_id = dialog_manager.event.from_user.id

    result = await update_task(
        task_id,
        {"description": text},
        user_id,
    )

    if result["error"]:
        await message.answer(
            ERROR_UPDATE_TASK.format(
                error=result["error"],
            )
        )
    else:
        await message.answer(SUCCESS_TASK_UPDATED)

    await dialog_manager.done()


async def on_category_updated(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    text: str,
) -> None:
    """Обработчик обновления категории задачи."""

    task_id = dialog_manager.dialog_data["task_id"]
    user_id = dialog_manager.event.from_user.id

    if text.lower() in ["пропустить", "skip", "-", "нет", "без категории"]:
        update_data = {"category": None}
    else:
        category_id = await find_or_create_category_id(text)
        if category_id:
            update_data = {"category_id": category_id}
        else:
            await message.answer(ERROR_CREATE_CATEGORY)
            return

    result = await update_task(
        task_id,
        update_data,
        user_id,
    )

    if result["error"]:
        await message.answer(
            ERROR_UPDATE_TASK.format(
                error=result["error"],
            )
        )
    else:
        await message.answer(SUCCESS_TASK_UPDATED)

    await dialog_manager.done()


async def on_end_date_updated(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    text: str,
) -> None:
    """Обработчик обновления даты завершения."""

    try:
        moscow_tz = ZoneInfo(TIMEZONE)
        end_dt = datetime.strptime(
            text,
            "%Y-%m-%d %H:%M",
        ).replace(tzinfo=moscow_tz)

        task_id = dialog_manager.dialog_data["task_id"]
        user_id = dialog_manager.event.from_user.id

        result = await update_task(
            task_id,
            {"end_date": end_dt.isoformat()},
            user_id,
        )

        if result["error"]:
            await message.answer(
                ERROR_UPDATE_TASK.format(
                    error=result["error"],
                ),
            )
        else:
            await message.answer(SUCCESS_TASK_UPDATED)

        await dialog_manager.done()
    except ValueError:
        await message.answer(ERROR_DATE_FORMAT)


async def on_edit_cancel(
    message: Message,
    button: Button,
    dialog_manager: DialogManager,
) -> None:
    """Обработчик отмены редактирования."""

    await message.answer(TASK_UPDATE_CANCELLED)
    await dialog_manager.done()


# Диалог редактирования задачи
edit_task_dialog = Dialog(
    Window(
        Const(SELECT_TASK_EDIT),
        Group(
            Select(
                id="task_select",
                items="task_choices",
                item_id_getter=lambda x: x[1],
                text=Format("{item[0]}"),
                on_click=on_task_selected_for_edit,
            ),
            width=1,
        ),
        Cancel(
            Const(BUTTON_CANCEL),
            on_click=on_edit_cancel,
        ),
        state=EditTaskStates.select_task,
        getter=get_tasks_for_editing,
    ),
    Window(
        Format(EDIT_TASK_HEADER),
        Column(
            Button(
                Const(BUTTON_EDIT_NAME),
                id="edit_name",
                on_click=on_name_edit_clicked,
            ),
            Button(
                Const(BUTTON_EDIT_DESCRIPTION),
                id="edit_description",
                on_click=on_description_edit_clicked,
            ),
            Button(
                Const(BUTTON_EDIT_CATEGORY),
                id="edit_category",
                on_click=on_category_edit_clicked,
            ),
            Button(
                Const(BUTTON_EDIT_END_DATE),
                id="edit_end_date",
                on_click=on_end_date_edit_clicked,
            ),
        ),
        Back(Const(BUTTON_BACK)),
        Cancel(
            Const(BUTTON_CANCEL),
            on_click=on_edit_cancel,
        ),
        state=EditTaskStates.choose_field,
        getter=get_task_data,
    ),
    Window(
        Const(TASK_NAME_PROMPT),
        TextInput(
            id="edit_name_input",
            on_success=on_name_updated,
        ),
        Back(Const(BUTTON_BACK)),
        Cancel(
            Const(BUTTON_CANCEL),
            on_click=on_edit_cancel,
        ),
        state=EditTaskStates.edit_name,
    ),
    Window(
        Const(TASK_DESCRIPTION_PROMPT),
        TextInput(
            id="edit_description_input",
            on_success=on_description_updated,
        ),
        Back(Const(BUTTON_BACK)),
        Cancel(
            Const(BUTTON_CANCEL),
            on_click=on_edit_cancel,
        ),
        state=EditTaskStates.edit_description,
    ),
    Window(
        Const(TASK_CATEGORY_PROMPT),
        TextInput(
            id="edit_category_input",
            on_success=on_category_updated,
        ),
        Back(Const(BUTTON_BACK)),
        Cancel(
            Const(BUTTON_CANCEL),
            on_click=on_edit_cancel,
        ),
        state=EditTaskStates.edit_category,
    ),
    Window(
        Const(TASK_END_DATE_PROMPT.format(timezone=TIMEZONE)),
        TextInput(
            id="edit_end_date_input",
            on_success=on_end_date_updated,
        ),
        Back(Const(BUTTON_BACK)),
        Cancel(
            Const(BUTTON_CANCEL),
            on_click=on_edit_cancel,
        ),
        state=EditTaskStates.edit_end_date,
    ),
)

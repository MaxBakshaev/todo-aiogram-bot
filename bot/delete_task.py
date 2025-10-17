from typing import Any
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Button, Cancel, Group, Select, Row

from utils import fetch_user_tasks, delete_task, fetch_single_task
from messages import (
    BUTTON_CANCEL,
    SUCCESS_TASK_DELETED,
    TASK_DELETION_CANCELLED,
    ERROR_LOAD_TASK,
    ERROR_DELETE_TASK,
    SELECT_TASK_DELETE,
    CONFIRM_DELETE,
    BUTTON_CONFIRM_DELETE,
    BUTTON_CANCEL_DELETE,
    NO_DESCRIPTION,
)
from states import DeleteTaskStates


async def get_tasks_for_deletion(
    dialog_manager: DialogManager,
    **kwargs,
) -> dict[str, Any]:
    """Получает задачи пользователя для выбора при удалении."""

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


async def on_task_selected_for_deletion(
    callback: CallbackQuery,
    widget: Select,
    dialog_manager: DialogManager,
    item_id: str,
) -> None:
    """Обработчик выбора задачи для удаления."""

    dialog_manager.dialog_data["task_id"] = item_id
    await dialog_manager.next()


async def get_selected_task_data(
    dialog_manager: DialogManager,
    **kwargs,
) -> dict | dict[str, Any]:
    """Получает данные выбранной задачи для подтверждения удаления."""

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
    return {
        "task_name": task.get("name", ""),
        "task_description": task.get(
            "description",
            "",
        )
        or NO_DESCRIPTION,
    }


async def on_deletion_confirmed(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
) -> None:
    """Обработчик подтверждения удаления."""

    task_id = dialog_manager.dialog_data["task_id"]
    user_id = dialog_manager.event.from_user.id

    result = await delete_task(
        task_id,
        user_id,
    )

    if result["error"]:
        await callback.message.answer(
            ERROR_DELETE_TASK.format(error=result["error"]),
        )
    else:
        await callback.message.answer(SUCCESS_TASK_DELETED)

    await dialog_manager.done()


async def on_deletion_cancelled(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
) -> None:
    """Обработчик отмены удаления."""

    await callback.message.answer(TASK_DELETION_CANCELLED)
    await dialog_manager.done()


# Диалог удаления задачи
delete_task_dialog = Dialog(
    Window(
        Const(SELECT_TASK_DELETE),
        Group(
            Select(
                id="task_select",
                items="task_choices",
                item_id_getter=lambda x: x[1],
                text=Format("{item[0]}"),
                on_click=on_task_selected_for_deletion,
            ),
            width=1,
        ),
        Cancel(
            Const(BUTTON_CANCEL),
            on_click=on_deletion_cancelled,
        ),
        state=DeleteTaskStates.select_task,
        getter=get_tasks_for_deletion,
    ),
    Window(
        Format(CONFIRM_DELETE),
        Row(
            Button(
                Const(BUTTON_CONFIRM_DELETE),
                id="confirm_delete",
                on_click=on_deletion_confirmed,
            ),
            Button(
                Const(BUTTON_CANCEL_DELETE),
                id="cancel_delete",
                on_click=on_deletion_cancelled,
            ),
        ),
        state=DeleteTaskStates.confirm,
        getter=get_selected_task_data,
    ),
)

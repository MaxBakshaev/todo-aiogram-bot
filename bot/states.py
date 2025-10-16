from aiogram.fsm.state import State, StatesGroup


class AddTaskStates(StatesGroup):
    name = State()
    description = State()
    category = State()
    end_date = State()


class EditTaskStates(StatesGroup):
    select_task = State()
    choose_field = State()
    edit_name = State()
    edit_description = State()
    edit_category = State()
    edit_end_date = State()


class DeleteTaskStates(StatesGroup):
    select_task = State()
    confirm = State()

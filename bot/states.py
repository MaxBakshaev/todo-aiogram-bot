from aiogram.fsm.state import State, StatesGroup


class AddTaskStates(StatesGroup):
    name = State()
    description = State()
    category = State()
    end_date = State()

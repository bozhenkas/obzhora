from aiogram.fsm.state import StatesGroup, State


class DataActions(StatesGroup):
    choosing_action = State()


class PollsForm(StatesGroup):
    waiting_for_department = State()
    viewing_polls = State()  # <-- Новое состояние

from aiogram.fsm.state import StatesGroup, State


class AddSumm(StatesGroup):
    choosing_summ = State()

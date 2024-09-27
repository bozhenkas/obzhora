# /data -> users, transactions, deleted_transactions, pidors
from datetime import datetime

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import FSInputFile
from keyboards.for_data import get_data_kb
from keyboards.for_choice import get_choice_kb
from methods import export_table_to_csv

router = Router()

with open('whitelist.txt', 'r') as file:
    wl = [int(line.strip()) for line in file.readlines() if line.strip().isdigit()]

ACTIONS = {
    "Основная таблица": "users",
    "Транзакции": "transactions",
    "Удалённые транзакции": "deleted_transactions",
}


class DataActions(StatesGroup):
    choosing_action = State()


@router.message(Command('data'))
async def cmd_data(message: types.Message, state: FSMContext):
    # Проверяем, есть ли ID пользователя в списке разрешенных
    if message.from_user.id not in wl:
        await message.answer("У вас нет доступа к этой команде.")
        with open('pidors.txt', 'a') as f:
            f.write(f'{str(message.from_user.id)} str(message.from_user.username)\n')
        return

    # Погружаем пользователя в состояние выбора действия
    await state.set_state(DataActions.choosing_action)

    # Отправляем сообщение с клавиатурой для выбора действия
    await message.answer("Выберите действие:", reply_markup=get_data_kb())


# Обработчик выбора действия в рамках состояния
@router.message(DataActions.choosing_action)
async def process_action(message: types.Message, state: FSMContext):
    user_input = message.text

    # Если пользователь нажал кнопку "⬅️ Назад"
    if user_input == "⬅️ Назад":
        await state.clear()  # очищаем состояние FSM
        await message.answer("Возврат в меню.", reply_markup=get_choice_kb())  # Возвращаем меню
        return

    # Если пользователь выбрал одно из действий (проверка по ACTIONS)
    if user_input == 'Пидорасы':
        await state.clear()
        await message.answer_document(FSInputFile('pidors.txt'))
    elif user_input in ACTIONS:
        table_name = ACTIONS[user_input]

        current_time = datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
        csv_file_path = f"csv_data/{table_name}_{current_time}.csv"
        await export_table_to_csv(table_name, csv_file_path)

        await message.answer_document(FSInputFile(csv_file_path))
    else:
        await message.answer("Ошибка: неизвестная команда. Пожалуйста, выберите одно из доступных действий:",
                             reply_markup=get_data_kb())

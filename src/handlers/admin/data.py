from datetime import datetime
import os
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile

from keyboards.for_data import get_data_kb
from keyboards.for_choice import get_choice_kb
from utils import export_table_to_csv
from database import db
from filters.curator_filter import CuratorFilter
from states import DataActions

router = Router()

ACTIONS = {
    "Основная таблица": "users",
    "Транзакции": "transactions",
    "Удалённые транзакции": "deleted_transactions",
}


@router.message(Command('data'), CuratorFilter())
async def cmd_data(message: types.Message, state: FSMContext):
    await state.set_state(DataActions.choosing_action)
    await message.answer("Выберите действие:", reply_markup=get_data_kb())


@router.message(DataActions.choosing_action, CuratorFilter())
async def process_action(message: types.Message, state: FSMContext):
    user_input = message.text

    if user_input == "⬅️ Назад":
        await state.clear()
        await message.answer("Возврат в меню.", reply_markup=get_choice_kb())
        return

    if user_input == 'Пидорасы':
        await state.clear()
        pidors_path = 'src/pidors.txt'
        if os.path.exists(pidors_path):
            await message.answer_document(FSInputFile(pidors_path))
        else:
            await message.answer(f"Файл '{pidors_path}' не найден. Убедитесь, что он лежит в корне проекта.")

    elif user_input in ACTIONS:
        await state.clear()
        table_name = ACTIONS[user_input]
        current_time = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        directory = "csv_data"
        if not os.path.exists(directory):
            os.makedirs(directory)
        csv_file_path = f"{directory}/{table_name}_{current_time}.csv"
        await export_table_to_csv(db, table_name, csv_file_path)
        await message.answer_document(FSInputFile(csv_file_path))

    else:
        await message.answer("Ошибка: неизвестная команда. Пожалуйста, выберите одно из доступных действий:",
                             reply_markup=get_data_kb())

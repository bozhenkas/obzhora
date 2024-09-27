import yaml
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardRemove

from keyboards.for_choice import get_choice_kb
from keyboards.for_categories import get_categories_kb
from keyboards.for_cancel import get_cancel_kb

from db_methods import add_transactions_to_bd
from methods import is_number

with open('handlers/txt.yml', 'r', encoding='utf-8') as file:
    data = yaml.safe_load(file)

router = Router()
available_categories = ['🍟 Mак', '🐔 KFC', '🍔 БК', '🍕🥦🥞 Другое']


class AddSumm(StatesGroup):
    choosing_summ = State()


@router.message(F.text.in_(available_categories))
async def msg_add_summ(message: types.Message, state: FSMContext):
    await state.update_data(chosen_category=message.text)
    await message.answer(data.get('summ_text'), reply_markup=get_cancel_kb())
    await state.set_state(AddSumm.choosing_summ)  # ставим состояние ввода суммы


# Обработка команды /cancel
@router.message(F.text == 'Отмена 🚫')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer(data.get('error_text'))
        return
    await state.clear()  # очищаем состояние FSM
    await message.answer(data.get('categories_text'), reply_markup=get_categories_kb())  # отправляем сообщение


@router.message(AddSumm.choosing_summ)
async def msg_add_summ(message: types.Message, state: FSMContext):
    if is_number(message.text):
        if float(message.text) > 0:
            category = await state.get_data()
            await add_transactions_to_bd(message.from_user.id, category['chosen_category'], float(message.text))
            await message.answer(data.get('complete_transaction_text'), reply_markup=get_choice_kb())
            await state.clear()  # сбрасываем состояние
        else:
            await message.answer(data.get('error_negative_number_text'), input_field_placeholder='Введи сумму')
    else:
        await message.answer(data.get('error_number_text'), input_field_placeholder='Введи сумму')

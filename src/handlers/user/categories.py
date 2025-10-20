import yaml
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from keyboards.for_choice import get_choice_kb
from keyboards.for_categories import get_categories_kb
from keyboards.for_cancel import get_cancel_kb
from database import db
from utils import is_number
from states import AddSumm
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
yaml_path = os.path.join(dir_path, '..', 'messages.yaml')

with open(yaml_path, 'r', encoding='utf-8') as file:
    data = yaml.safe_load(file)

router = Router()
available_categories = ['🍟 Mак', '🐔 KFC', '🍔 БК', '🍕🥦🥞 Другое']


@router.message(F.text.in_(available_categories))
async def msg_add_summ(message: types.Message, state: FSMContext):
    await state.update_data(chosen_category=message.text)
    await message.answer(data.get('summ_text'), reply_markup=get_cancel_kb())
    await state.set_state(AddSumm.choosing_summ)


@router.message(F.text == 'Отмена 🚫', AddSumm.choosing_summ)
async def cancel_handler(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(data.get('categories_text'), reply_markup=get_categories_kb())


@router.message(AddSumm.choosing_summ)
async def msg_process_summ(message: types.Message, state: FSMContext):
    if is_number(message.text):
        if float(message.text) > 0:
            user_data = await state.get_data()
            await db.add_transaction(message.from_user.id, user_data['chosen_category'], float(message.text))
            await message.answer(data.get('complete_transaction_text'), reply_markup=get_choice_kb())
            await state.clear()
        else:
            await message.answer(data.get('error_negative_number_text'), input_field_placeholder='Введи сумму')
    else:
        await message.answer(data.get('error_number_text'), input_field_placeholder='Введи сумму')

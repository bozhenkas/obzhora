import yaml
from aiogram import Router, F, types
from aiogram.types import ReplyKeyboardRemove

from keyboards.for_choice import get_choice_kb
from keyboards.for_transactions import (get_transactions_kb, confirm_delete_kb,
                                        choice_selection_kb, back21_kb, back17_kb)
from database import db
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
yaml_path = os.path.join(dir_path, '..', 'messages.yaml')

with open(yaml_path, 'r', encoding='utf-8') as file:
    data = yaml.safe_load(file)

router = Router()


@router.message(F.text == '🧾 Транзакции')
async def msg_transactions(message: types.Message):
    user_data = await db.get_user_data(message.from_user.id)
    keyboard = await get_transactions_kb(message.from_user.id)

    await message.answer(data.get('transactions_emoji'), reply_markup=ReplyKeyboardRemove())

    total_sum = user_data['summ'] if user_data else 0
    await message.answer(f'{data.get("transactions_text_1")} <b>{total_sum}</b> ₽ \n \n'
                         f'{data.get("transactions_text_2")}', reply_markup=keyboard, disable_notification=True)


@router.callback_query(F.data.startswith(("transaction_", "confirmFalse_", "back21_")))
async def callbacks_selections(callback: types.CallbackQuery):
    action = callback.data.split("_")[1]
    keyboard = await choice_selection_kb(callback, action)
    transaction_text = await db.get_transaction_by_id(int(action))
    await callback.message.edit_text(transaction_text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith('action_delete_'))
async def request_delete_confirmation(callback: types.CallbackQuery):
    action = callback.data.split("_")[2]
    keyboard = await confirm_delete_kb(callback, action)
    await callback.message.edit_text(data.get("delete_text"), reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith('confirmTrue_'))
async def confirm_delete(callback: types.CallbackQuery):
    action = callback.data.split("_")[1]
    keyboard = await back17_kb(callback)
    if await db.delete_transaction_by_id(int(action)):
        await callback.message.edit_text(data.get("success_delete_text"), reply_markup=keyboard)
    else:
        await callback.message.edit_text(data.get("failing_delete_text"), reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith('action_edit_'))
async def edit_action(callback: types.CallbackQuery):
    action = callback.data.split("_")[2]
    keyboard = await back21_kb(callback, action)
    await callback.message.edit_text(data.get("edit_text"), reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith('back5'))
async def back_to_menu(callback: types.CallbackQuery):
    await callback.message.answer(data.get("menu_text"), reply_markup=get_choice_kb())
    await callback.message.delete()
    await callback.answer()


@router.callback_query(F.data.startswith('back17'))
async def back_to_transactions(callback: types.CallbackQuery):
    user_data = await db.get_user_data(callback.from_user.id)
    keyboard = await get_transactions_kb(callback.from_user.id)
    total_sum = user_data['summ'] if user_data else 0
    await callback.message.edit_text(f'{data.get("transactions_text_1")} <b>{total_sum}</b> ₽ \n \n'
                                     f'{data.get("transactions_text_2")}', reply_markup=keyboard,
                                     disable_notification=True)
    await callback.answer()

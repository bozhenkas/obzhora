import yaml
from aiogram import Router, F, types
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardRemove


from keyboards.for_choice import get_choice_kb
from keyboards.for_transactions import get_transactions_kb, confirm_delete_kb, choice_selection_kb, back21_kb, back17_kb

from db_methods import delete_transaction_by_id, get_transaction_by_id, get_user_data

with open('handlers/txt.yml', 'r', encoding='utf-8') as file:
    data = yaml.safe_load(file)

router = Router()


class TransactionSelection(StatesGroup):
    transaction_output = State()
    transaction_select = State()


@router.message(F.text == '🧾 Транзакции')
async def msg_transactions(message: types.Message):
    transactions_summ = await get_user_data(message.from_user.id)
    keyboard = await get_transactions_kb(message.from_user.id)
    # Тут мы подгрузили всю инлайн клавиатуру из файлика
    await message.answer(data.get('transactions_emoji'), reply_markup=ReplyKeyboardRemove())
    await message.answer(f'{data.get("transactions_text_1")} <b>{transactions_summ[-1]}</b> ₽ \n \n'
                         f'{data.get("transactions_text_2")}', reply_markup=keyboard, disable_notification=True)


@router.callback_query(F.data.startswith("transaction_"))
@router.callback_query(F.data.startswith("confirmFalse_"))
@router.callback_query(F.data.startswith('back21_'))
async def callbacks_selections(callback: types.CallbackQuery):
    action = callback.data.split("_")[1]
    print(action)
    keyboard = await choice_selection_kb(callback, action)
    await callback.message.edit_text(await get_transaction_by_id(int(action)),
                                     reply_markup=keyboard)  # сюда запрос в бд по номеру action
    await callback.answer()


@router.callback_query(F.data.startswith('action_delete_'))
async def go_back(callback: types.CallbackQuery):
    action = callback.data.split("_")[2]
    keyboard = await confirm_delete_kb(callback, action)
    await callback.message.edit_text(data.get("delete_text"), reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith('confirmTrue_'))
async def go_back(callback: types.CallbackQuery):
    action = callback.data.split("_")[1]
    keyboard = await back17_kb(callback)
    if await delete_transaction_by_id(int(action)):
        await callback.message.edit_text(data.get("success_delete_text"), reply_markup=keyboard)
    else:
        await callback.message.edit_text(data.get("failing_delete_text"), reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith('action_edit_'))
async def go_back(callback: types.CallbackQuery):
    action = callback.data.split("_")[2]
    keyboard = await back21_kb(callback, action)
    await callback.message.edit_text(data.get("edit_text"), reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith('back5'))
async def go_back(callback: types.CallbackQuery):
    await callback.message.answer(data.get("menu_text"), reply_markup=get_choice_kb())
    await callback.message.delete()
    await callback.answer()


@router.callback_query(F.data.startswith('back17'))
async def msg_transactions(callback: types.CallbackQuery):
    transactions_summ = await get_user_data(callback.from_user.id)
    keyboard = await get_transactions_kb(callback.from_user.id)
    # Тут мы подгрузили всю инлайн клавиатуру из файлика
    await callback.message.edit_text(f'{data.get("transactions_text_1")} <b>{transactions_summ[-1]}</b> ₽ \n \n'
                                     f'{data.get("transactions_text_2")}', reply_markup=keyboard,
                                     disable_notification=True)
    await callback.answer()

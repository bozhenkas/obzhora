from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton

from db_methods import get_user_data, get_transactions, get_transaction_by_id
from methods import transaction_to_inline, transactions_to_list


async def get_transactions_kb(user_id: int):
    transactions_list = await transactions_to_list(await get_transactions(user_id))
    transactions_strings = await transaction_to_inline(transactions_list)
    buttons = []
    for i in range(len(transactions_strings)):
        element = transactions_strings[i]
        index = transactions_list[i][0]
        button = [InlineKeyboardButton(text=str(element), callback_data=f'transaction_{index}')]
        buttons.append(button)
    button = [InlineKeyboardButton(text='⬅️ Назад', callback_data='back5_')]
    buttons.append(button)
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


async def confirm_delete_kb(callback: types.CallbackQuery, action):
    buttons = [[InlineKeyboardButton(text='Подтвердить', callback_data=f'confirmTrue_{action}'),
                InlineKeyboardButton(text='Отмена', callback_data=f'confirmFalse_{action}')]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


async def choice_selection_kb(callback: types.CallbackQuery, action):
    buttons = [
        [InlineKeyboardButton(text='Удалить', callback_data=f'action_delete_{action}')],
        # InlineKeyboardButton(text='Редактировать', callback_data=f'action_edit_{action}')],
        [InlineKeyboardButton(text='⬅️ Назад', callback_data=f'back17_{action}')]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


async def back21_kb(callback: types.CallbackQuery, action):
    buttons = [[InlineKeyboardButton(text='⬅️ Назад', callback_data=f'back21_{action}')]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


async def back17_kb(callback: types.CallbackQuery):
    buttons = [[InlineKeyboardButton(text='⬅️ Назад', callback_data=f'back17_')]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

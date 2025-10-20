from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton

from database import db
from utils import reverse_refactor_category, format_datetime


async def get_transactions_kb(user_id: int):
    transactions_records = await db.get_user_transactions(user_id)

    buttons = []
    for record in transactions_records:
        category = reverse_refactor_category(record['category'])
        date_str = format_datetime(record['date'])

        text = f"{record['summ']} ₽ | {category} | {date_str}"

        button = [InlineKeyboardButton(text=text, callback_data=f'transaction_{record["id"]}')]
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

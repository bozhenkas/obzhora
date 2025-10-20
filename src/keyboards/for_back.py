from aiogram import types


def get_back_kb():
    k = [
        [types.KeyboardButton(text='⬅️ Назад')]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=k,
        resize_keyboard=True,
    )
    return keyboard

from aiogram import types


def get_data_kb():
    k = [
        [types.KeyboardButton(text='Основная таблица')],
        [types.KeyboardButton(text='Транзакции'), types.KeyboardButton(text='Удалённые транзакции')],
        [types.KeyboardButton(text='Пидорасы')],
        [types.KeyboardButton(text='⬅️ Назад')]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=k,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие",
    )
    return keyboard

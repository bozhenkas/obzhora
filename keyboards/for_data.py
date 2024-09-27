from aiogram import types


# жёстко отдельный файл для создания трёх кнопок...

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
        input_field_placeholder="хуй",
    )
    return keyboard

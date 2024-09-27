from aiogram import types


# жёстко отдельный файл для создания одной кнопки...

def get_cancel_kb():
    k = [
        [types.KeyboardButton(text='Отмена 🚫')]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=k,
        resize_keyboard=True,
        input_field_placeholder='десять миллионов тыщ'
    )
    return keyboard

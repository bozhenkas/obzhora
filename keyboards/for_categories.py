from aiogram import types


# жёстко отдельный файл для создания трёх кнопок...

def get_categories_kb():
    k = [
        [types.KeyboardButton(text='🍟 Mак'), types.KeyboardButton(text='🐔 KFC'), types.KeyboardButton(text='🍔 БК')],
        [types.KeyboardButton(text='🍕🥦🥞 Другое')],
        [types.KeyboardButton(text='⬅️ Назад')]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=k,
        resize_keyboard=True,
        input_field_placeholder="нажми на кнопочку",
    )
    return keyboard

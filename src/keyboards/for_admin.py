# src/keyboards/admin_keyboards.py

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData


# Используем CallbackData для чистоты кода
class AddAdminCallback(CallbackData, prefix="add_admin"):
    action: str = "add"


def get_add_admin_kb() -> InlineKeyboardMarkup:
    """
    Создает инлайн-клавиатуру для добавления администратора.
    Читает файл whitelist.txt для получения актуального счетчика.
    """
    whitelist_path = 'whitelist.txt'  # Путь относительно корня /app в Docker
    count = 0
    try:
        with open(whitelist_path, 'r') as f:
            # Считаем только непустые строки, в которых есть числа
            admin_ids = {int(line.strip()) for line in f if line.strip().isdigit()}
            count = len(admin_ids)
    except FileNotFoundError:
        # Если файл не найден, счетчик равен 0
        pass

    button_text = f"✅ Стать админом ({count} в списке)"

    button = InlineKeyboardButton(
        text=button_text,
        callback_data=AddAdminCallback().pack()
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button]])
    return keyboard

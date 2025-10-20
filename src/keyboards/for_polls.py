import logging
from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List


# ... (код get_departments_kb и класс PollsCallback остаются без изменений) ...
def get_departments_kb():
    k = [
        [types.KeyboardButton(text='Общая'), types.KeyboardButton(text='Тынцы')],
        [types.KeyboardButton(text='Музыка'), types.KeyboardButton(text='Сценарный отдел')],
        [types.KeyboardButton(text='Декорации'), types.KeyboardButton(text='Медиа-отдел')],
        [types.KeyboardButton(text='⬅️ Назад')]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=k, resize_keyboard=True, input_field_placeholder="выберите отдел",
    )
    return keyboard


class PollsCallback(CallbackData, prefix="poll_page"):
    action: str
    page: int


# --- НАЧАЛО ИЗМЕНЕНИЙ С ЛОГИРОВАНИЕМ ---
def get_polls_pagination_kb(polls_data: List[dict], page: int = 0) -> InlineKeyboardMarkup:
    logging.info(f"--- ГЕНЕРАЦИЯ КЛАВИАТУРЫ ПАГИНАЦИИ ---")
    total_pages = len(polls_data)
    logging.info(f"Получены параметры: page={page}, total_pages={total_pages}")

    buttons = []
    nav_buttons = []

    if page > 0:
        prev_page_data = PollsCallback(action="prev", page=page - 1).pack()
        logging.info(f"Создаю кнопку 'Назад' с callback_data: '{prev_page_data}'")
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=prev_page_data))

    nav_buttons.append(InlineKeyboardButton(text=f"{page + 1}/{total_pages}", callback_data="do_nothing"))

    if page < total_pages - 1:
        next_page_data = PollsCallback(action="next", page=page + 1).pack()
        logging.info(f"Создаю кнопку 'Вперед' с callback_data: '{next_page_data}'")
        nav_buttons.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=next_page_data))

    buttons.append(nav_buttons)
    buttons.append([InlineKeyboardButton(text="✅ Закрыть", callback_data=PollsCallback(action="close", page=0).pack())])

    logging.info("--- ГЕНЕРАЦИЯ КЛАВИАТУРЫ ЗАВЕРШЕНА ---\n")
    return InlineKeyboardMarkup(inline_keyboard=buttons)

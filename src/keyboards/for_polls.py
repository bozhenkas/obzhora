from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List


def get_departments_kb():
    k = [
        [types.KeyboardButton(text='Общая'), types.KeyboardButton(text='Тынцы')],
        [types.KeyboardButton(text='Музыка'), types.KeyboardButton(text='Сценарный отдел')],
        [types.KeyboardButton(text='Декорации'), types.KeyboardButton(text='Медиа-отдел')],
        [types.KeyboardButton(text='⬅️ Назад')]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=k,
        resize_keyboard=True,
        input_field_placeholder="выберите отдел",
    )
    return keyboard


class PollsCallback(CallbackData, prefix="poll_page"):
    action: str  # "prev", "next", "close"
    page: int


def get_polls_pagination_kb(polls_data: List[dict], page: int = 0) -> InlineKeyboardMarkup:
    total_pages = len(polls_data)
    buttons = []

    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=PollsCallback(action="prev", page=page - 1).pack()
            )
        )

    nav_buttons.append(
        InlineKeyboardButton(
            text=f"{page + 1}/{total_pages}",
            callback_data="do_nothing"
        )
    )

    if page < total_pages - 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text="Вперед ➡️",
                callback_data=PollsCallback(action="next", page=page + 1).pack()
            )
        )

    buttons.append(nav_buttons)

    # Кнопка для закрытия
    buttons.append([
        InlineKeyboardButton(
            text="✅ Закрыть",
            callback_data=PollsCallback(action="close", page=0).pack()
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

import logging
import yaml
import os
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from typing import List, Dict, Any
from utils import get_non_voters_from_vk
from keyboards.for_polls import get_departments_kb, get_polls_pagination_kb, PollsCallback
from keyboards.for_choice import get_choice_kb
from filters.curator_filter import CuratorFilter
from states import PollsForm

router = Router()

dir_path = os.path.dirname(os.path.realpath(__file__))
yaml_path = os.path.join(dir_path, '..', 'messages.yaml')
with open(yaml_path, 'r', encoding='utf-8') as file:
    MESSAGES = yaml.safe_load(file)

ACTIONS = {
    "Общая": "general", "Тынцы": "dance", "Музыка": "music",
    "Сценарный отдел": "script", "Декорации": "decorations", "Медиа-отдел": "media"
}


async def _get_poll_page_content(polls_data: List[Dict[str, Any]], page: int) -> tuple[str, types.InlineKeyboardMarkup]:
    current_poll = polls_data[page]
    total_pages = len(polls_data)
    text = ""
    if current_poll.get("error") == "tech_account_not_voted":
        text_template = MESSAGES['poll_tech_account_error_text']
        text = text_template.format(poll_question=current_poll["question"], current_page=page + 1,
                                    total_pages=total_pages)
    else:
        if current_poll.get("students_non_voters_links") == "отсутствуют.":
            text_template = MESSAGES['poll_no_students_text']
        else:
            text_template = MESSAGES['poll_result_text']
        text = text_template.format(
            poll_question=current_poll.get("question", "Без названия"), current_page=page + 1, total_pages=total_pages,
            total_non_voters=current_poll.get("total_non_voters", 0),
            curators_non_voters_count=current_poll.get("curators_non_voters_count", 0),
            students_non_voters_links=current_poll.get("students_non_voters_links", "нет данных")
        )
    keyboard = get_polls_pagination_kb(polls_data, page)
    return text, keyboard


@router.message(Command("polls"), CuratorFilter())
async def cmd_polls(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(PollsForm.waiting_for_department)
    await message.answer("Выберите отдел:", reply_markup=get_departments_kb())


@router.message(PollsForm.waiting_for_department, F.text.in_(ACTIONS))
async def process_department_selection(message: types.Message, state: FSMContext):
    msg = await message.answer("Скрипт выполняется, ищу опросы и проверяю тех. аккаунт...")
    polls_data = await get_non_voters_from_vk(ACTIONS[message.text])
    if not polls_data:
        await msg.edit_text(
            f'🎉 Все проголосовали во всех опросах отдела <b>"{message.text}"</b>, либо опросы не найдены!')
        await state.clear()
        return

    logging.info(f"Сохраняем в FSM данные по опросам. Количество опросов: {len(polls_data)}")
    await state.update_data(polls=polls_data, department_name=message.text)
    await state.set_state(PollsForm.viewing_polls)

    text, keyboard = await _get_poll_page_content(polls_data, page=0)
    await msg.edit_text(text, reply_markup=keyboard)


@router.message(PollsForm.waiting_for_department, F.text == '⬅️ Назад')
async def process_back_from_polls_choice(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Возврат в меню.", reply_markup=get_choice_kb())


@router.message(PollsForm.waiting_for_department)
async def process_unknown_department(message: types.Message):
    await message.answer("Пожалуйста, выберите действительный отдел с помощью кнопок.")


@router.callback_query(PollsCallback.filter(F.action.in_(["prev", "next"])))
async def navigate_polls_callback(callback: types.CallbackQuery, callback_data: PollsCallback, state: FSMContext):
    logging.info("--- СРАБОТАЛ ХЭНДЛЕР ПАГИНАЦИИ (БЕЗ ПРОВЕРКИ СОСТОЯНИЯ) ---")
    logging.info(f"Получен callback: action='{callback_data.action}', page='{callback_data.page}'")

    await callback.answer()

    fsm_data = await state.get_data()
    logging.info(f"Данные из FSM (состояния): {fsm_data}")

    polls_data = fsm_data.get("polls", [])

    if not polls_data:
        logging.error("Критическая ошибка: данные 'polls' в FSM не найдены!")
        await callback.message.edit_text("Ошибка: данные для пагинации не найдены. Попробуйте заново.")
        return

    logging.info(f"Успешно извлечено {len(polls_data)} опросов из FSM.")
    page = callback_data.page
    total_pages = len(polls_data)

    if not 0 <= page < total_pages:
        logging.warning(f"Ошибка: неверный номер страницы. page={page}, total_pages={total_pages}")
        await callback.message.edit_text("Ошибка: неверный номер страницы. Попробуйте заново.")
        return

    logging.info(f"Формирую контент для страницы {page + 1}/{total_pages}")
    text, keyboard = await _get_poll_page_content(polls_data, page)

    try:
        await callback.message.edit_text(text, reply_markup=keyboard)
        logging.info(f"Сообщение успешно отредактировано для страницы {page + 1}")
    except Exception as e:
        logging.error(f"Не удалось отредактировать сообщение: {e}")
        await callback.message.answer("Не удалось обновить старое сообщение. Попробуйте вызвать команду заново.")
    logging.info("--- КОНЕЦ ОБРАБОТКИ ПАГИНАЦИИ ---\n")


@router.callback_query(PollsCallback.filter(F.action == "close"))
async def close_polls_view_callback(callback: types.CallbackQuery, state: FSMContext):
    logging.info("--- СРАБОТАЛ ХЭНДЛЕР ЗАКРЫТИЯ (БЕЗ ПРОВЕРКИ СОСТОЯНИЯ) ---")
    await callback.answer("Закрыто.")
    await callback.message.delete()
    await state.clear()

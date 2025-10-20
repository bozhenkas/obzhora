# obzhora/src/utils.py

import csv
import httpx
import asyncio
from datetime import datetime
from typing import List, Any, TYPE_CHECKING, Dict

from config import config, VK_API_URL

if TYPE_CHECKING:
    from database import Database

DEPARTMENTS = {
    'general': 'Общая || Кубок Ректора || ИТПИ || 2025',
    'dance': 'Танцы || Кубок Ректора || ИТПИ || 2025',
    'music': 'Музыка || Кубок Ректора || ИТПИ || 2025',
    'script': 'Сценарный отдел || Кубок Ректора || ИТПИ || 2025',
    'decorations': 'Декорации || Кубок Ректора || ИТПИ || 2025',
    'media': 'Медиа-отдел || Кубок Ректора || ИТПИ || 2025'
}


async def get_non_voters_from_vk(department: str) -> List[Dict[str, Any]]:
    """
    Получает список опросов с информацией о непроголосовавших.
    Возвращает список словарей, где каждый словарь - это один опрос.
    """
    chat_name = DEPARTMENTS.get(department)
    if not chat_name:
        return []

    async with httpx.AsyncClient(timeout=30.0) as client:
        # --- НОВАЯ ВНУТРЕННЯЯ ФУНКЦИЯ ---
        async def _get_self_id():
            """Получает ID технического аккаунта."""
            try:
                res = await client.post(f"{VK_API_URL}users.get", data={**config.vk_default_data})
                return res.json().get('response', [{}])[0].get('id')
            except Exception:
                return None

        # --- КОНЕЦ НОВОЙ ФУНКЦИИ ---

        async def _get_conversations():
            res = await client.post(f"{VK_API_URL}messages.getConversations",
                                    data={"count": 200, **config.vk_default_data})
            response_data = res.json().get('response', {})
            if not response_data:
                return []
            return [c for c in response_data.get('items', []) if
                    'chat_settings' in c['conversation'] and chat_name in c['conversation']['chat_settings']['title']]

        async def _get_history(peer_id):
            tasks = [client.post(f"{VK_API_URL}messages.getHistory",
                                 data={'peer_id': peer_id, 'offset': offset, 'count': 200, **config.vk_default_data})
                     for offset in [0, 200, 400]]
            pages = await asyncio.gather(*tasks)
            return [item for page in pages for item in page.json().get('response', {}).get('items', [])]

        async def _get_members(peer_id):
            res = await client.post(f"{VK_API_URL}messages.getConversationMembers",
                                    data={'peer_id': peer_id, **config.vk_default_data})
            return res.json().get('response', {}).get('items', [])

        async def _get_voters(poll_id, answer_ids):
            tasks = [client.post(f"{VK_API_URL}polls.getVoters",
                                 data={'poll_id': poll_id, 'answer_ids': answer_id, **config.vk_default_data}) for
                     answer_id in answer_ids]
            responses = await asyncio.gather(*tasks)
            return {user_id for res in responses for item in res.json().get('response', []) for user_id in
                    item.get('users', {}).get('items', [])}

        tech_account_id, conversations = await asyncio.gather(_get_self_id(), _get_conversations())

        if not conversations:
            return []
        if not tech_account_id:
            # Если не удалось получить ID тех. аккаунта, возвращаем ошибку для всех опросов
            # Это маловероятно, но лучше обработать
            return [{"question": "Не удалось проверить технический аккаунт", "error": "tech_account_fetch_failed"}]

        all_polls_data = []
        for conv in conversations:
            peer_id = conv['conversation']['peer']['id']
            history, members_data = await asyncio.gather(_get_history(peer_id), _get_members(peer_id))
            member_ids = {member['member_id'] for member in members_data if member['member_id'] > 0}
            polls = [att['poll'] for msg in history if msg.get('attachments') for att in msg['attachments'] if
                     att.get('type') == 'poll']

            for poll in polls:
                answer_ids = [ans['id'] for ans in poll['answers']]
                voted_ids = await _get_voters(poll['id'], answer_ids)

                # --- КЛЮЧЕВАЯ ПРОВЕРКА ---
                if tech_account_id not in voted_ids:
                    poll_info = {
                        "question": poll["question"],
                        "error": "tech_account_not_voted"  # Специальный флаг ошибки
                    }
                    all_polls_data.append(poll_info)
                    continue  # Переходим к следующему опросу
                # --- КОНЕЦ ПРОВЕРКИ ---

                non_voted_ids = member_ids - voted_ids

                if non_voted_ids:
                    curators_non_voted = {uid for uid in non_voted_ids if uid in config.curators_list}
                    students_non_voted = non_voted_ids - curators_non_voted

                    students_links = ', '.join([f'@id{user_id}' for user_id in students_non_voted])

                    poll_info = {
                        "question": poll["question"],
                        "total_non_voters": len(non_voted_ids),
                        "curators_non_voters_count": len(curators_non_voted),
                        "students_non_voters_links": students_links if students_links else "отсутствуют."
                    }
                    all_polls_data.append(poll_info)

    return all_polls_data


# ... (остальные функции в файле остаются без изменений) ...

def format_datetime(dt_obj: datetime) -> str:
    months = ('января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября',
              'декабря')
    return f"{dt_obj.day} {months[dt_obj.month - 1]} в {dt_obj.strftime('%H:%M')}"


def refactor_category(category: str) -> str:
    category_map = {'🍟 Mак': 'vit', '🐔 KFC': 'kfc', '🍔 БК': 'bk', '🍕🥦🥞 Другое': 'other'}
    if category in category_map:
        return category_map[category]
    raise ValueError(f"Недопустимая категория: {category}")


def reverse_refactor_category(category_key: str) -> str:
    category_map = {'vit': '🍟 Mак', 'kfc': '🐔 KFC', 'bk': '🍔 БК', 'other': '🍕🥦🥞 Другое'}
    if category_key in category_map:
        return category_map[category_key]
    raise ValueError(f"Недопустимый ключ категории: {category_key}")


def is_number(value: Any) -> bool:
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False


async def export_table_to_csv(db: 'Database', table_name: str, csv_file_path: str):
    headers, data = await db.fetch_all_from_table(table_name)
    if not headers or not data:
        if headers:
            with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(headers)
        return

    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(headers)
        writer.writerows([tuple(row.values()) for row in data])

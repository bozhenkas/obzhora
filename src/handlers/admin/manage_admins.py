from aiogram import Router, F, types
from aiogram.filters import Command

from filters.curator_filter import CuratorFilter
from keyboards.for_admin import get_add_admin_kb, AddAdminCallback

router = Router()
WHITELIST_PATH = 'src/whitelist.txt'


@router.message(
    Command('add_admins'),
    CuratorFilter(),
    F.chat.type.in_({'group', 'supergroup'})
)
async def cmd_add_admins(message: types.Message):
    """
    Хэндлер для команды /add_admins. Работает только для админов в группах.
    Отправляет сообщение с кнопкой для добавления в whitelist.
    """
    text = (
        "кто не нажмет, тот лох"
    )
    await message.answer(text, reply_markup=get_add_admin_kb())


@router.callback_query(AddAdminCallback.filter())
async def callback_add_admin(callback: types.CallbackQuery):
    """
    Обрабатывает нажатие на кнопку "Стать админом".
    Добавляет ID пользователя в whitelist.txt и обновляет кнопку.
    """
    user_id = callback.from_user.id

    # Читаем текущий список админов, используя set для избежания дубликатов
    try:
        with open(WHITELIST_PATH, 'r') as f:
            admin_ids = {int(line.strip()) for line in f if line.strip().isdigit()}
    except FileNotFoundError:
        admin_ids = set()

    # Проверяем, есть ли пользователь уже в списке
    if user_id in admin_ids:
        await callback.answer("Вы уже в списке администраторов.", show_alert=True)
    else:
        # Добавляем нового админа и перезаписываем файл
        admin_ids.add(user_id)
        with open(WHITELIST_PATH, 'w') as f:
            for admin_id in sorted(list(admin_ids)):
                f.write(f"{admin_id}\n")

        await callback.answer("Вы успешно добавлены в список администраторов!", show_alert=True)

        # Обновляем сообщение с кнопкой, чтобы счетчик изменился
        try:
            await callback.message.edit_reply_markup(reply_markup=get_add_admin_kb())
        except Exception as e:
            # Может возникнуть ошибка, если сообщение слишком старое, просто логируем
            print(f"Не удалось обновить клавиатуру: {e}")

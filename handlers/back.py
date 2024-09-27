import yaml
from aiogram import Router, F, types
from keyboards.for_choice import get_choice_kb

with open('handlers/txt.yml', 'r', encoding='utf-8') as file:
    data = yaml.safe_load(file)
router = Router()


@router.message(F.text == '⬅️ Назад')
async def msg_go_back(message: types.Message):
    await message.answer(data.get('menu_text'), reply_markup=get_choice_kb())

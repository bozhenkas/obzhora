import yaml
from aiogram import Router, types
from aiogram.filters.command import Command

from db_methods import add_to_db
from keyboards.for_choice import get_choice_kb

with open('handlers/txt.yml', 'r', encoding='utf-8') as file:
    data = yaml.safe_load(file)

router = Router()


@router.message(Command('start'))
async def cmd_start(message: types.Message):
    await add_to_db(message.from_user.id, message.from_user.username)
    await message.answer(data.get('start_text'), reply_markup=get_choice_kb())

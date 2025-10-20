import yaml
from aiogram import Router, types
from aiogram.filters.command import Command

from database import db
from keyboards.for_choice import get_choice_kb
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
yaml_path = os.path.join(dir_path, '..', 'messages.yaml')

with open(yaml_path, 'r', encoding='utf-8') as file:
    data = yaml.safe_load(file)

router = Router()


@router.message(Command('start'))
async def cmd_start(message: types.Message):
    await db.add_user(message.from_user.id, message.from_user.username)
    await message.answer(data.get('start_text'), reply_markup=get_choice_kb())

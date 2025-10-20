import yaml
from aiogram import Router, F, types
from keyboards.for_choice import get_choice_kb
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
yaml_path = os.path.join(dir_path, '..', 'messages.yaml')

with open(yaml_path, 'r', encoding='utf-8') as file:
    data = yaml.safe_load(file)
router = Router()


@router.message(F.text == '⬅️ Назад')
async def msg_go_back(message: types.Message):
    await message.answer(data.get('menu_text'), reply_markup=get_choice_kb())

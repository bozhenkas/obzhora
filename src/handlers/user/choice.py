import yaml
from aiogram import Router, F, types

from keyboards.for_back import get_back_kb
from keyboards.for_categories import get_categories_kb
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
yaml_path = os.path.join(dir_path, '..', 'messages.yaml')

with open(yaml_path, 'r', encoding='utf-8') as file:
    data = yaml.safe_load(file)

router = Router()


@router.message(F.text == '💵 Добавить сумму')
async def msg_add_summ(message: types.Message):
    await message.answer(data.get('categories_text'), reply_markup=get_categories_kb())


@router.message(F.text == 'ℹ️ Информация')
async def msg_information(message: types.Message):
    await message.answer(data.get('information_text'), reply_markup=get_back_kb())

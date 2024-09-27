import datetime
import pytz

from aiogram import Router, types
from aiogram.filters.command import Command

from db_methods import get_total_summ
from methods import format_datetime

router = Router()
# Чтение whitelist.txt и получение списка разрешенных ID
with open('whitelist.txt', 'r') as file:
    wl = [int(line.strip()) for line in file.readlines() if line.strip().isdigit()]


@router.message(Command('total'))
async def cmd_total(message: types.Message):
    if message.from_user.id in wl:
        date = datetime.datetime.now(pytz.timezone('Europe/Moscow')).strftime("%Y-%m-%d %H:%M:%S %Z")[:-4]
        time = format_datetime(date)
        await message.answer(f'Общая сумма на {time}:\n'
                             f'<b>{await get_total_summ()} ₽</b>')
    else:
        await message.answer("У вас нет доступа к этой команде.")
        with open('pidors.txt', 'a') as f:
            f.write(f'{str(message.from_user.id)} str(message.from_user.username)\n')

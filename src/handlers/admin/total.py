import datetime
import pytz
from aiogram import Router, types
from aiogram.filters.command import Command

from database import db
from utils import format_datetime
from filters.curator_filter import CuratorFilter

router = Router()


@router.message(Command('total'), CuratorFilter())
async def cmd_total(message: types.Message):
    now_utc = datetime.datetime.now(pytz.utc)
    time_str = format_datetime(now_utc)
    total_sum = await db.get_total_summ()

    await message.answer(f'Общая сумма на {time_str}:\n<b>{total_sum} ₽</b>')

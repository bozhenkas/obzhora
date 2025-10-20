from typing import Union
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

try:
    with open('src/whitelist.txt', 'r') as f:
        curators = {int(line.strip()) for line in f if line.strip().isdigit()}
except FileNotFoundError:
    print("ВНИМАНИЕ: Файл 'whitelist.txt' не найден. Админ-команды не будут работать.")
    curators = set()


class CuratorFilter(BaseFilter):
    async def __call__(self, event: Union[Message, CallbackQuery]) -> bool:
        return event.from_user.id in curators

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage
from contextlib import asynccontextmanager
from redis.asyncio import Redis

from config import config
from database import db
from handlers import start, choice, back, categories, transactions, total, data, polls, manage_admins


@asynccontextmanager
async def lifespan(dp: Dispatcher, bot: Bot):
    await db.connect()
    yield
    await db.close()
    await dp.storage.close()


async def main():
    bot = Bot(token=config.bot_token.get_secret_value(), default=DefaultBotProperties(parse_mode='HTML'))

    redis = Redis(host=config.redis_host, port=config.redis_port)
    storage = RedisStorage(redis=redis)

    dp = Dispatcher(storage=storage)

    dp.include_routers(
        start.router,
        choice.router,
        back.router,
        categories.router,
        transactions.router,
        total.router,
        data.router,
        polls.router,
        manage_admins.router,
    )

    await bot.delete_webhook(drop_pending_updates=True)
    async with lifespan(dp, bot):
        await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

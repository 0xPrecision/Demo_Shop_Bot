import asyncio
import logging
from config_data.bot_instance import bot
from aiogram import Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from bot.handlers.admin_handlers import router as admin_router
from bot.handlers.user_handlers import router as user_router
from database.init_db import init_db, close_db


async def main():
    """
    Главная точка входа бота: инициализация БД, запуск бота, корректное закрытие соединений.
    """
    storage = RedisStorage.from_url("redis://localhost:6379/0")
    logging.basicConfig(level=logging.INFO)
    await init_db()
    dp = Dispatcher(storage=storage)
    dp.include_router(admin_router)
    dp.include_router(user_router)
    print('Бот запущен!')
    try:
        await dp.start_polling(bot)
    finally:
        await close_db()

if __name__ == "__main__":
    asyncio.run(main())
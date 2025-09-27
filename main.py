import asyncio
import logging
from pathlib import Path

from aiogram import Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

from bot.handlers.admin_handlers import router as admin_router
from bot.handlers.user_handlers import router as user_router
from config_data.bot_instance import bot
from database.init_db import close_db, init_db
from services.i18n.middleware import LocaleMiddleware
from services.i18n.translations import Translator
from services.locale_repo import LocaleRepo


async def main():
    """
    Main entry point of the bot: initializes the database, starts the bot,
    and properly closes connections.
    """
    storage = RedisStorage.from_url("redis://localhost:6379/0")
    logging.basicConfig(level=logging.INFO)
    await init_db()

    translator = Translator(
        locales_dir=Path("/Users/stsaw/PycharmProjects/Demo_Shop_Bot/services/locales"),
        default_locale="ru",
        supported=("ru", "en"),
    )
    locale_repo = LocaleRepo()
    dp = Dispatcher(storage=storage)
    dp.update.middleware.register(LocaleMiddleware(translator, locale_repo))
    dp.include_router(admin_router)
    dp.include_router(user_router)
    print("Bot started!")
    try:
        await dp.start_polling(bot)
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(main())

from config_data.env import TELEGRAM_BOT_TOKEN
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties


bot = Bot(
    token=TELEGRAM_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode='HTML')
)
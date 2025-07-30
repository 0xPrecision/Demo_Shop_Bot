import inspect

from aiogram import Router
from aiogram.types import Message, CallbackQuery
from typing import Callable
from config_data.env import ADMIN_IDS


router = Router()


def is_admin(user_id: int) -> bool:
    """
    Проверяет, является ли пользователь админом по user_id.
    :param user_id: Telegram user ID.
    :return: True, если админ.
    """
    return user_id in ADMIN_IDS

def admin_only(handler: Callable) -> Callable:
    """
    Декоратор для ограничения доступа только для админов.
    Можно вешать на любые admin-хэндлеры.
    """
    async def wrapper(*args, **kwargs):
        event = args[0]
        user_id = getattr(event.from_user, "id", None) if hasattr(event, "from_user") else getattr(event.message.from_user, "id", None)
        if not is_admin(user_id):
            if isinstance(event, Message):
                await event.answer("❌ У вас нет доступа к админ-командам.")
            elif isinstance(event, CallbackQuery):
                await event.answer("❌ Нет доступа.", show_alert=True)
            return

        sig = inspect.signature(handler)
        allowed_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
        return await handler(*args[:len(sig.parameters)], **allowed_kwargs)

    return wrapper

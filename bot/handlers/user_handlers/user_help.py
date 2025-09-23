from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from bot.keyboards.user.user_main_menu import main_menu
from bot.utils.common_utils import delete_request_and_user_message

router = Router()

async def help_cmd(callback: CallbackQuery, state: FSMContext):
    """
    Sends the user a help message about the store operation.
	"""
    await delete_request_and_user_message(callback.message, state)
    await callback.bot.send_message(
        callback.from_user.id,
        "🛒 <b>Это демо-магазин в Telegram!</b>\n\n"
        "Доступные действия:\n"
        "• <b>Каталог</b> — посмотреть товары по категориям\n"
        "• <b>Корзина</b> — посмотреть, что вы добавили, оформить заказ\n"
        "• <b>Профиль</b> — ваши контактные данные и заказы\n\n"
        "Если возникли вопросы или нужна поддержка — пишите нашему администратору.",
        reply_markup=main_menu()
    )


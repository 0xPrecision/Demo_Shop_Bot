from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.keyboards.user.user_main_menu import main_menu

router = Router()

@router.message(F.text == "/start")
async def start_cmd(message: Message, state: FSMContext):
    """
    Обработчик команды /start — показывает инлайн главное меню.
    """
    await state.clear()
    await message.answer(
        "<b>Добро пожаловать в магазин!</b>\n"
        "Выберите действие:",
        reply_markup=main_menu()
    )


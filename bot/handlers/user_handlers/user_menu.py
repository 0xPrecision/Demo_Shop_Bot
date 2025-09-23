from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.handlers.user_handlers.user_catalog import show_categories
from bot.handlers.user_handlers.user_cart import show_cart
from bot.handlers.user_handlers.user_help import help_cmd
from bot.handlers.user_handlers.user_profile import show_profile_menu
from bot.utils.user_utils.user_common_utils import delete_user_message_safe
from bot.utils.user_utils.universal_handlers import universal_exit

router = Router()


@router.callback_query(lambda c: c.data in ["menu_main", "menu_catalog"])
async def universal_exit_handler(callback: CallbackQuery, state: FSMContext):
    """
    Universal handler for exiting any state via the “Main Menu” and “Catalog” buttons.
	"""
    await universal_exit(callback, state)


@router.callback_query(F.data.startswith("menu_"))
async def menu_router(callback: CallbackQuery, state: FSMContext):
    """
    Routes clicks across the main menu sections.
	"""
    action = callback.data.replace("menu_", "")
    await callback.message.delete()
    if action == "catalog":
        await show_categories(callback)
    elif action == "cart":
        await show_cart(callback, state)
    elif action == "profile":
        await show_profile_menu(callback)
    elif action == "help":
        await help_cmd(callback, state)

    await callback.answer()


@router.message(F.text)
async def text_catch_all_handler(message: Message, state: FSMContext):
    """
    Catches any text when only a callback button is expected.
    Shows an alert and does not change the FSM state.
	"""
    if message.text != '/start_admin':
        await delete_user_message_safe(message)
        msg = await message.answer("Пожалуйста, используйте кнопки выше 👆")
        await state.update_data(main_message_id=msg.message_id)

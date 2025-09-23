from aiogram import Router, F
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from bot.keyboards.admin.admin_menu import admin_main_menu
from .admin_access import admin_only

router = Router()


@router.message(or_f(F.text == "/start_admin", F.data == "/start_admin"))
@router.callback_query(or_f(F.data == "/start_admin", F.text == "/start_admin"))
@admin_only
async def admin_panel_open(event: Message | CallbackQuery, state: FSMContext):
    """
    Generic handler for opening the admin menu.
    Works for both messages and callback buttons.
	"""
    await state.clear()
    if hasattr(event, "message"):  # CallbackQuery
        msg = event.message
        edit = True
    else:  # Message
        msg = event
        edit = False

    if edit:
        await msg.edit_text(
            "👑 Админ-панель\nВыберите действие:",
            reply_markup=admin_main_menu()
        )
        await event.answer()
    else:
        await msg.answer(
            "👑 Админ-панель\nВыберите действие:",
            reply_markup=admin_main_menu()
        )


@router.message(F.text == '/start_admin')
@admin_only
async def admin_panel_message(message: Message, state: FSMContext):
    await admin_panel_open(message, state)

@router.callback_query(F.data == "/start_admin")
@admin_only
async def admin_panel_callback(callback: CallbackQuery, state: FSMContext):
    await admin_panel_open(callback, state)
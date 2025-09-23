from aiogram import Router, F
from aiogram.types import CallbackQuery
from .admin_access import admin_only
from ...keyboards.admin.help_keyboard import help_keyboard
router = Router()

@router.callback_query(F.data == 'admin_help')
@admin_only
async def admin_help(callback: CallbackQuery):
    """
    Sends help about the admin panel features and quick links.
	"""
    text = t('admin_help.misc.b-admin-panel-pomosch-b-b-osnovnye')
    await callback.message.edit_text(text, reply_markup=help_keyboard())
    await callback.answer()
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.handlers.admin_handlers.admin_access import admin_only
from bot.keyboards.admin.admin_menu import admin_main_menu
from bot.keyboards.admin.catalog_keyboards import confirm_deletion_product
from bot.utils.common_utils import delete_request_and_user_message
from database.models import Product

router = Router()


@router.callback_query(F.data.startswith("admin_delete_product:"))
@admin_only
async def delete_product_confirm(callback: CallbackQuery, state: FSMContext):
    """
    Подтверждение удаления товара.
    """
    await delete_request_and_user_message(callback.message, state)
    product_id = int(callback.data.split(":")[1])
    msg = await callback.message.answer("Вы уверены, что хотите удалить этот товар?",
                                     reply_markup=confirm_deletion_product(product_id))
    await state.update_data(main_message_id=msg.message_id)
    await callback.answer()

@router.callback_query(F.data.startswith("admin_delete_product_yes:"))
@admin_only
async def delete_product_execute(callback: CallbackQuery):
    """
    Удаляет товар из базы (или делает неактивным).
    """
    product_id = int(callback.data.split(":")[1])
    await Product.filter(id=product_id).update(is_active=False)
    await callback.message.edit_text("Товар удалён.", reply_markup=admin_main_menu())
    await callback.answer()

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from database.crud import update_category
from database.models import Category
from database.models import Product
from .admin_access import admin_only
from ...keyboards.admin.catalog_keyboards import confirm_deletion_category, edit_or_deletion_category, back_menu
from ...states.admin_states.category_states import CategoryEditStates
from ...utils.common_utils import delete_request_and_user_message
router = Router()

@router.callback_query(F.data.startswith('admin_edit_category:'))
@admin_only
async def choose_category_to_edit(callback: CallbackQuery, t, **_):
    """
    Selects an option for the category.
	"""
    category_id = int(callback.data.split(':', 1)[1])
    await callback.message.edit_text(t('admin_catalog.messages.vyberete-dejstvie'), reply_markup=edit_or_deletion_category(category_id, t))

@router.callback_query(F.data.startswith('admin_rename_category_select:'))
@admin_only
async def rename_category_start(callback: CallbackQuery, t, state: FSMContext, **_):
    """
    Starts the FSM to enter a new category name.
	"""
    cat_id = int(callback.data.split(':')[1])
    await state.update_data(rename_category_id=cat_id)
    msg = await callback.message.edit_text(t('edit_category.messages.vvedite-novoe-nazvanie-dlya'))
    await state.update_data(main_message_id=msg.message_id)
    await state.set_state(CategoryEditStates.renaming)
    await callback.answer()

@router.message(CategoryEditStates.renaming)
@admin_only
async def rename_category_process(message: Message, t, state: FSMContext, **_):
    """
    Takes the new category name and saves it to the database.
	"""
    await delete_request_and_user_message(message, state)
    new_name = message.text.strip()
    data = await state.get_data()
    cat_id = data.get('rename_category_id')
    if not new_name:
        msg = await message.answer(t('edit_category.messages.nazvanie-ne-mozhet-byt'), reply_markup=back_menu(t))
        await state.update_data(main_message_id=msg.message_id)
        return
    exists = await Category.filter(name=new_name).exists()
    if exists:
        msg = await message.answer(t('edit_category.messages.kategoriya-s-takim-imenem'), reply_markup=back_menu(t))
        await state.update_data(main_message_id=msg.message_id)
        return
    await update_category(cat_id, new_name)
    msg = await message.answer(f'Категория успешно переименована в «{new_name}» ✅', reply_markup=back_menu(t))
    await state.update_data(main_message_id=msg.message_id)
    await state.clear()

@router.callback_query(F.data.startswith('admin_delete_category_select:'))
@admin_only
async def delete_category_confirm(callback: CallbackQuery, t, **_):
    """
    Checks whether the category can be deleted (no products inside) and requests confirmation.
	"""
    cat_id = int(callback.data.split(':')[1])
    count = await Product.filter(category_id=cat_id).count()
    if count > 0:
        await callback.answer(t('edit_category.messages.v-kategorii-est-tovary'), show_alert=True)
        return
    category = await Category.get(id=cat_id)
    await callback.message.edit_text(f'Вы уверены, что хотите удалить категорию «{category.name}»?', reply_markup=confirm_deletion_category(cat_id, t))
    await callback.answer()

@router.callback_query(F.data.startswith('admin_delete_category_yes:'))
@admin_only
async def delete_category_execute(callback: CallbackQuery, t, **_):
    """
    Deletes the category from the database (if it has no products).
	"""
    cat_id = int(callback.data.split(':')[1])
    await Category.filter(id=cat_id).delete()
    await callback.message.edit_text(t('edit_category.messages.kategoriya-udalena'), reply_markup=back_menu(t))
    await callback.answer()
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


@router.callback_query(F.data.startswith("admin_edit_category:"))
@admin_only
async def choose_category_to_edit(callback: CallbackQuery):
    """
    Выбор опции для категории.
    """
    category_id = int(callback.data.split(":", 1)[1])
    await callback.message.edit_text("Выберете действие:",
                                     reply_markup=edit_or_deletion_category(category_id))



@router.callback_query(F.data.startswith("admin_rename_category_select:"))
@admin_only
async def rename_category_start(callback: CallbackQuery, state: FSMContext):
    """
    Запускает FSM для ввода нового имени категории.
    """
    cat_id = int(callback.data.split(":")[1])
    await state.update_data(rename_category_id=cat_id)
    msg = await callback.message.edit_text("Введите новое название для категории:")
    await state.update_data(main_message_id=msg.message_id)
    await state.set_state(CategoryEditStates.renaming)
    await callback.answer()


@router.message(CategoryEditStates.renaming)
@admin_only
async def rename_category_process(message: Message, state: FSMContext):
    """
    Получает новое имя категории и сохраняет в базе.
    """
    await delete_request_and_user_message(message, state)
    new_name = message.text.strip()
    data = await state.get_data()
    cat_id = data.get("rename_category_id")
    if not new_name:
        msg = await message.answer("Название не может быть пустым.", reply_markup=back_menu())
        await state.update_data(main_message_id=msg.message_id)
        return

    # Проверка на уникальность
    exists = await Category.filter(name=new_name).exists()
    if exists:
        msg = await message.answer("Категория с таким именем уже существует.", reply_markup=back_menu())
        await state.update_data(main_message_id=msg.message_id)
        return

    await update_category(cat_id, new_name)
    msg = await message.answer(f"Категория успешно переименована в «{new_name}» ✅", reply_markup=back_menu())
    await state.update_data(main_message_id=msg.message_id)
    await state.clear()



@router.callback_query(F.data.startswith("admin_delete_category_select:"))
@admin_only
async def delete_category_confirm(callback: CallbackQuery):
    """
    Проверяет, можно ли удалить категорию (нет ли в ней товаров), и просит подтверждение.
    """
    cat_id = int(callback.data.split(":")[1])
    count = await Product.filter(category_id=cat_id).count()
    if count > 0:
        await callback.answer("В категории есть товары! Сначала перенесите или удалите их.", show_alert=True)
        return

    category = await Category.get(id=cat_id)
    await callback.message.edit_text(
        f"Вы уверены, что хотите удалить категорию «{category.name}»?",
        reply_markup=confirm_deletion_category(cat_id)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_delete_category_yes:"))
@admin_only
async def delete_category_execute(callback: CallbackQuery):
    """
    Удаляет категорию из базы (если нет товаров).
    """
    cat_id = int(callback.data.split(":")[1])
    await Category.filter(id=cat_id).delete()
    await callback.message.edit_text("Категория удалена.", reply_markup=back_menu())
    await callback.answer()

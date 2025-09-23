from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from database.crud import get_product_by_id, update_product, get_all_categories
from bot.keyboards.admin.catalog_keyboards import product_edit_field_keyboard, create_or_cancel_edit_product_kb, \
    change_category_keyboard, back_menu
from database.models import Category
from .admin_access import admin_only
from ...states.admin_states.product_states import EditProductStates
from ...utils.common_utils import delete_request_and_user_message, format_price

router = Router()


@router.callback_query(F.data.startswith("admin_edit_product:"))
@admin_only
async def edit_product_start(callback: CallbackQuery, state: FSMContext):
    """
    Displays an inline keyboard to choose the field to edit.
	"""
    await delete_request_and_user_message(callback.message, state)
    product_id = int(callback.data.split(":")[1])
    product = await get_product_by_id(product_id)
    await state.update_data(edit_product_id=product_id, edit_fields={})
    await show_edit_product_summary(callback.message, product, state)
    msg = await callback.message.answer(
        "Что хотите изменить?",
        reply_markup=product_edit_field_keyboard(product_id)
    )
    await state.update_data(main_message_id=msg.message_id)
    await state.set_state(EditProductStates.choosing_field)
    await callback.answer()


@router.callback_query(EditProductStates.choosing_field, F.data.startswith("edit_field:"))
@admin_only
async def choose_edit_field(callback: CallbackQuery, state: FSMContext):
    """
    Starts editing the selected field.
	"""
    await delete_request_and_user_message(callback.message, state)
    _, field, product_id = callback.data.split(":")
    await state.update_data(editing_field=field)
    if field == "category":
        categories = await get_all_categories()
        msg = await callback.message.answer(
            "Выберите новую категорию:",
            reply_markup=change_category_keyboard(categories)
        )
        await state.update_data(main_message_id=msg.message_id)
        await state.set_state(EditProductStates.editing_category)
    elif field == "photo":
        msg = await callback.message.answer("Отправьте новое фото товара:")
        await state.update_data(main_message_id=msg.message_id)
        await state.set_state(EditProductStates.editing_field)
    elif field == "confirm":
        data = await state.get_data()
        product_id = data.get("edit_product_id")
        product = await get_product_by_id(product_id)
        edit_fields = data.get("edit_fields", {})
        # Генерируем summary
        await show_edit_product_summary(callback.message, product, state, edit_fields)
        # Подтверждение (да/нет)
        msg = await callback.message.answer("Подтвердить изменения?",
                                      reply_markup=create_or_cancel_edit_product_kb())
        await state.update_data(main_message_id=msg.message_id)
        await state.set_state(EditProductStates.confirming)
    else:
        field_names = {
            "name": "новое название",
            "price": "новую цену",
            "description": "новое описание",
            "stock": "новый остаток"
        }
        msg = await callback.message.answer(f"Введите {field_names[field]} товара:")
        await state.update_data(main_message_id=msg.message_id)
        await state.set_state(EditProductStates.editing_field)
    await callback.answer()


@router.message(EditProductStates.editing_field)
@admin_only
async def process_edit_field(message: Message, state: FSMContext):
    """
    Processes the new value of the selected field.
	"""
    await delete_request_and_user_message(message, state)
    data = await state.get_data()
    field = data.get("editing_field")
    edit_fields = data.get("edit_fields", {})

    if field == "name":
        edit_fields["name"] = message.text.strip()
    elif field == "price":
        try:
            price = float(message.text.replace(",", ".").strip())
            if price <= 0: raise ValueError
            edit_fields["price"] = price
        except ValueError:
            msg = await message.answer("Введите корректную цену!")
            await state.update_data(main_message_id=msg.message_id)
            return
    elif field == "description":
        edit_fields["description"] = message.text.strip()
    elif field == "stock":
        try:
            stock = int(message.text.strip())
            if stock < 0: raise ValueError
            edit_fields["stock"] = stock
        except ValueError:
            msg = await message.answer("Введите корректный остаток!")
            await state.update_data(main_message_id=msg.message_id)
            return
    elif field == "photo" and message.photo:
        edit_fields["photo"] = message.photo[-1].file_id
    else:
        msg = await message.answer("Пожалуйста, повторите ввод.")
        await state.update_data(main_message_id=msg.message_id)
        return

    await state.update_data(edit_fields=edit_fields)
    product_id = data.get("edit_product_id")
    product = await get_product_by_id(product_id)
    await show_edit_product_summary(message, product, state, edit_fields)
    msg = await message.answer("Что хотите изменить дальше?",
                         reply_markup=product_edit_field_keyboard(product_id))
    await state.update_data(main_message_id=msg.message_id)
    await state.set_state(EditProductStates.choosing_field)


@router.callback_query(EditProductStates.editing_category)
@admin_only
async def edit_category_callback(callback: CallbackQuery, state: FSMContext):
    """
    Handles the selection of a new category.
	"""
    await delete_request_and_user_message(callback.message, state)
    category_id = callback.data.replace("change_category:", "")
    data = await state.get_data()
    edit_fields = data.get("edit_fields", {})
    edit_fields["category_id"] = category_id
    await state.update_data(edit_fields=edit_fields)
    product_id = data.get("edit_product_id")
    product = await get_product_by_id(product_id)
    await show_edit_product_summary(callback.message, product, state, edit_fields)
    msg = await callback.message.answer("Что хотите изменить дальше?",
                                  reply_markup=product_edit_field_keyboard(product_id))
    await state.update_data(main_message_id=msg.message_id)
    await state.set_state(EditProductStates.choosing_field)
    await callback.answer()


@router.callback_query(EditProductStates.confirming, F.data == "edit_save")
@admin_only
async def save_product_edits(callback: CallbackQuery, state: FSMContext):
    """
    Saves the changes to the product.
	"""
    await delete_request_and_user_message(callback.message, state)
    data = await state.get_data()
    product_id = data.get("edit_product_id")
    edit_fields = data.get("edit_fields", {})
    if not edit_fields:
        await callback.answer("Нет изменений для сохранения.", show_alert=True)
        return
    # Получаем название категории, если была изменена
    if "category_id" in edit_fields:
        category_obj = await Category.get(id=edit_fields["category_id"])
        edit_fields["category"] = category_obj
        del edit_fields["category_id"]
    await update_product(product_id, **edit_fields)
    msg = await callback.message.answer("Изменения успешно сохранены ✅",
                                        reply_markup=back_menu())
    await delete_summary(callback.message, state)
    await state.update_data(main_message_id=msg.message_id)
    await state.clear()
    await callback.answer()


async def show_edit_product_summary(message_or_callback, product, state, edit_fields: dict = None):
    """
    Sends the product summary (including changes) with a photo (if any).
	"""
    await delete_summary(message_or_callback, state)
    await product.fetch_related("category")
    data = {
        "name": product.name,
        "price": product.price,
        "description": product.description,
        "stock": product.stock,
        "photo": product.photo,
        "category": product.category.name if product.category else "-"
    }
    if edit_fields:
        data.update(edit_fields)
        if "category_id" in data:
            cat = await Category.get(id=data["category_id"])
            data["category"] = cat.name
        elif isinstance(data.get("category"), Category):
            data["category"] = data["category"].name
        elif isinstance(data.get("category"), str):
            pass
        else:
            data["category"] = "-"

    text = (
        f"<b>Товар:</b>\n"
        f"<b>{data['name']}</b>\n"
        f"Цена: {format_price(data['price'])}₽\n"
        f"Описание: {data['description'] or '—'}\n"
        f"Остаток: {data['stock']}\n"
        f"Категория: {data['category']}\n"
    )
    if data.get("photo"):
        try:
            msg = await message_or_callback.bot.send_photo(
                chat_id=message_or_callback.chat.id,
                photo=data["photo"],
                caption=text,
            )
            await state.update_data(summary_message_id=msg.message_id)
        except Exception:
            msg = await message_or_callback.answer(text)
            await state.update_data(summary_message_id=msg.message_id)
    else:
        msg = await message_or_callback.answer(text)
    await state.update_data(summary_message_id=msg.message_id)


async def delete_summary(message, state):
    """
    Function to delete the summary.
	"""
    data = await state.get_data()
    summary_message_id = data.get('summary_message_id')
    if summary_message_id:
        try:
            await message.bot.delete_message(message.chat.id, summary_message_id)
        except Exception:
            pass
        await state.update_data(summary_message_id=None)



from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from .admin_access import admin_only
from database.models import Product
from ...keyboards.admin.catalog_keyboards import product_admin_keyboard, show_products_for_search, \
    back_to_search_keyboard
from ...states.admin_states.product_states import ProductSearchStates
from ...utils.common_utils import format_price, delete_request_and_user_message

router = Router()


@router.callback_query(F.data == "admin_search_product")
@admin_only
async def start_search_product(callback: CallbackQuery, state: FSMContext):
    """
    Запускает FSM поиска товара.
    """
    msg = await callback.message.edit_text("🔍 Введите название товара или его ID для поиска:")
    await state.update_data(main_message_id=msg.message_id)
    await state.set_state(ProductSearchStates.waiting_query)
    await callback.answer()


@router.message(ProductSearchStates.waiting_query)
@admin_only
async def search_product_query(message: Message, state: FSMContext):
    """
    Ищет товар по введённому тексту или ID.
    """
    await delete_request_and_user_message(message, state)
    query = message.text.strip()
    # Сначала пробуем как ID
    if query.isdigit():
        products = await Product.filter(id=int(query)).all()
    else:
        products = await Product.filter(name__icontains=query).all()
    if not products:
        msg = await message.answer("Ничего не найдено. Попробуйте другой запрос или вернитесь назад.",
                             reply_markup=back_to_search_keyboard())
        await state.update_data(main_message_id=msg.message_id)
        await state.clear()
        return
    # Если один товар — сразу подробная карточка
    if len(products) == 1:
        product = products[0]
        await product.fetch_related("category")

        text = (
            f"Название: <b>{product.name}</b>\n"
            f"Цена: {format_price(product.price)} ₽\n"
            f"Описание: {product.description or '—'}\n"
            f"Остаток: {product.stock}\n"
            f"Категория: {product.category.name if product.category else '-'}"
        )
        if product.photo:
            await message.bot.send_photo(
                chat_id=message.chat.id,
                photo=product.photo,
                caption=text,
                reply_markup=product_admin_keyboard(product.id)
            )
        else:
            msg = await message.answer(text, reply_markup=product_admin_keyboard(product.id))
            await state.update_data(main_message_id=msg.message_id)
        await state.clear()
    else:
        # Несколько — делаем список с кнопками

        await message.answer(f"Найдено товаров: {len(products)}\nВыберите для просмотра:",
                             reply_markup=show_products_for_search(products))
        await state.clear()

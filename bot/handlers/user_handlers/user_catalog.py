from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram import Router, F
from database.crud import get_all_products
from database.models import Product
from bot.utils.common_utils import paginate, format_price, delete_request_and_user_message
from bot.keyboards.user.user_main_menu import main_menu
from bot.keyboards.user.user_catalog_keyboards import show_product_info_kb, products_keyboard, show_categories_keyboard

router = Router()
PAGE_SIZE = 5


async def show_categories(callback: CallbackQuery) -> None:
    """
    Показывает список категорий товаров.
    """
    products = await get_all_products()
    categories = sorted({p.category.name for p in products if p.category is not None})
    if not categories:
        await callback.message.answer("Категории не найдены.", reply_markup=main_menu())
        return
    await callback.message.answer(
        "Выберите категорию:",
        reply_markup=show_categories_keyboard(categories)
    )

@router.callback_query(F.data.startswith("category_"))
async def show_products_in_category(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Показывает товары выбранной категории с пагинацией.
    """
    await delete_request_and_user_message(callback.message, state)
    data = callback.data.split("_", 2)
    category_name = data[1]
    page = int(data[2]) if len(data) > 2 else 0
    all_products = await get_all_products()
    # Фильтруем по названию категории
    category_products = [p for p in all_products if (p.category and p.category.name == category_name)]
    if not category_products:
        await callback.message.edit_text("В этой категории пока нет товаров.", reply_markup=main_menu())
        await callback.answer()
        return

    page_products, total_pages, current_page = paginate(category_products, page, PAGE_SIZE)
    text = f"<b>🛍Товары в категории «{category_name}»</b>\n"
    text += "-" * 42
    text += "\n\nЧтобы узнать подробнее о товаре, нажмите на его название."

    markup = products_keyboard(page_products, category_name, current_page, total_pages)

    msg = await callback.message.answer(
        text,
        reply_markup=markup
    )
    await state.update_data(main_message_id=msg.message_id)
    await callback.answer()


@router.callback_query(F.data.startswith("product_"))
async def show_product_info(callback: CallbackQuery):
    """
    Универсальный хэндлер для отображения подробной информации о товаре,
    различает источник (catalog/cart) по callback_data.
    """
    try:
        parts = callback.data.split("_")
        product_id = int(parts[1])
        source = parts[2]
        category_name = parts[3] if len(parts) > 3 else None
        page = parts[4] if len(parts) > 4 else 0
    except (IndexError, ValueError):
            await callback.answer("Ошибка. Некорректный товар.", show_alert=True)
            return

    product = await Product.get_or_none(id=product_id)
    if not product:
        await callback.answer("Товар не найден.", show_alert=True)
        return

    if product.photo:
        await callback.message.delete()
        await callback.bot.send_photo(
            chat_id=callback.message.chat.id,
            photo=product.photo,
            caption=(
                f"<b>{product.name}</b>\n"
                f"Цена: {format_price(product.price)} ₽\n"
                f"Описание: {product.description or 'Нет описания.'}"
            ),
            reply_markup=show_product_info_kb(product.id, source, category_name, page),
        )
    else:
        await callback.message.edit_text(
            text=(
                f"<b>{product.name}</b>\n"
                f"Цена: {format_price(product.price)} ₽\n"
                f"Описание: {product.description or 'Нет описания.'}"
            ),
            reply_markup=show_product_info_kb(product.id, source, category_name, page)
        )
    await callback.answer()



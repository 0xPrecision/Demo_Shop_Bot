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

async def show_categories(callback: CallbackQuery, t, **_) -> None:
    """
    Displays the list of product categories.
	"""
    products = await get_all_products()
    categories = sorted({p.category.name for p in products if p.category is not None})
    if not categories:
        await callback.message.answer(t('user_catalog.messages.kategorii-ne-najdeny'), reply_markup=main_menu(t))
        return
    await callback.message.answer(t('user_catalog.messages.vyberite-kategoriyu'), reply_markup=show_categories_keyboard(categories, t))

@router.callback_query(F.data.startswith('category_'))
async def show_products_in_category(callback: CallbackQuery, t, state: FSMContext, **_) -> None:
    """
    Displays products of the selected category with pagination.
	"""
    await delete_request_and_user_message(callback.message, state)
    data = callback.data.split('_', 2)
    category_name = data[1]
    page = int(data[2]) if len(data) > 2 else 0
    all_products = await get_all_products()
    category_products = [p for p in all_products if p.category and p.category.name == category_name]
    if not category_products:
        await callback.message.edit_text(t('user_catalog.messages.v-etoj-kategorii-poka'), reply_markup=main_menu(t))
        await callback.answer()
        return
    page_products, total_pages, current_page = paginate(category_products, page, PAGE_SIZE)
    text = (
            t("category.header").format(category_name=category_name)
            + t("category.separator")
            + t("category.hint")
    )
    markup = products_keyboard(page_products, category_name, current_page, total_pages, t)
    msg = await callback.message.answer(text, reply_markup=markup)
    await state.update_data(main_message_id=msg.message_id)
    await callback.answer()

@router.callback_query(F.data.startswith('product_'))
async def show_product_info(callback: CallbackQuery, t, **_):
    """
    Generic handler for displaying product details,
    distinguishes the source (catalog/cart) by callback_data.
	"""
    try:
        parts = callback.data.split('_')
        product_id = int(parts[1])
        source = parts[2]
        category_name = parts[3] if len(parts) > 3 else None
        page = parts[4] if len(parts) > 4 else 0
    except (IndexError, ValueError):
        await callback.answer(t('user_catalog.messages.nekorrektnyj-tovar'), show_alert=True)
        return

    product = await Product.get_or_none(id=product_id)

    if not product:
        await callback.answer(t('admin_catalog.messages.tovar-ne-najden'), show_alert=True)
        return

    caption = (
        t("product.card.caption")
        .format(
            name=product.name,
            price=format_price(product.price),
            currency="₽",
            description=product.description or t("product.card.no_description")
        )
    )
    kb = show_product_info_kb(product.id, source, t, category_name, page)

    if product.photo:
        await callback.message.delete()
        await callback.bot.send_photo(
            chat_id=callback.message.chat.id,
            photo=product.photo,
            caption=caption,
            reply_markup=kb
        )

    else:
        await callback.message.edit_text(
            text=caption,
            reply_markup=kb
        )

    await callback.answer()
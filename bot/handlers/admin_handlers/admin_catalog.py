from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from bot.keyboards.admin.catalog_keyboards import product_admin_keyboard, admin_catalog_menu_keyboard, show_products_or_edit_category
from database.models import Category
from ...utils.admin_utils.catalog_utils import get_products_info, filter_or_change_pr_category
from database.crud import get_products_page, get_product_by_id, get_products_page_by_category
from .admin_access import admin_only
from ...utils.common_utils import format_price, delete_request_and_user_message
router = Router()

@router.callback_query(F.data == 'admin_catalog')
@admin_only
async def admin_catalog_menu(callback: CallbackQuery, t, **_):
    """
    Catalog main menu: choose between products and categories.
	"""
    await callback.message.edit_text(t('admin_catalog.messages.chto-vy-hotite-prosmotret-redaktirovat'), reply_markup=admin_catalog_menu_keyboard(t))
    await callback.answer()

@router.callback_query(F.data == 'admin_products')
@admin_only
async def admin_products_list(callback: CallbackQuery, state: FSMContext, t):
    """
    Displays the first page of products.
	"""
    await delete_request_and_user_message(callback.message, state)
    page = 1
    text = t('spisok-tovarov')
    func = get_products_page(page)
    await get_products_info(callback, t, page, text, func, state)
    await callback.answer()

@router.callback_query(F.data == 'admin_categories')
@admin_only
async def admin_categories_entry(callback: CallbackQuery, state: FSMContext, t):
    """
    Displays an inline keyboard for selecting a product category (filter).
	"""
    text = t('admin_catalog.misc.kategorii-tovarov-vyberite-dlya')
    await filter_or_change_pr_category(callback, state, t, text)
    await callback.answer()

@router.callback_query(F.data.startswith('admin_products_page:'))
@admin_only
async def admin_products_page(callback: CallbackQuery, state: FSMContext, t):
    """
    Paginates through catalog pages.
	"""
    page = int(callback.data.split(':')[1])
    text = t('admin_catalog.misc.b-tovary-b-str').format(page=page)
    func = get_products_page(page)
    await get_products_info(callback, t, page, text, func, state)
    await callback.answer()

@router.callback_query(F.data.startswith('admin_product_detail:'))
@admin_only
async def admin_product_detail(callback: CallbackQuery, t, state: FSMContext, **_):
    """
    Displays product details and an admin keyboard.
	"""
    product_id = int(callback.data.split(':')[1])
    product = await get_product_by_id(product_id)
    await product.fetch_related('category')
    if not product:
        await callback.answer(t('admin_catalog.messages.tovar-ne-najden'), show_alert=True)
        return
    product_name = product.name
    stock = product.stock
    category = product.category.name if product.category else '—'
    pr_price = format_price(product.price)
    pr_descr = product.description or '—'
    text = t('admin_catalog.misc.b-tovar-b-b-b-ostatok-kategoriya').format(product_name=product_name,
                                                                           pr_category=category,
                                                                           description=pr_descr,
                                                                           price=pr_price,
                                                                           currency="₽",
                                                                           stock=stock)
    if product.photo:
        msg = await callback.message.answer_photo(photo=product.photo, caption=text, reply_markup=await product_admin_keyboard(product_id, t))
        await callback.message.delete()
        await state.update_data(main_message_id=msg.message_id)
    else:
        msg = await callback.message.edit_text(text=text, reply_markup=await product_admin_keyboard(product_id, t))
        await state.update_data(main_message_id=msg.message_id)
    await callback.answer()

@router.callback_query(F.data.startswith('admin_select_category:'))
@admin_only
async def admin_products_by_category(callback: CallbackQuery, t, **_):
    """
    Displays options for the selected category.
	"""
    category_id = int(callback.data.split(':', 1)[1])
    await callback.message.edit_text(t('admin_catalog.messages.vyberete-dejstvie'), reply_markup=show_products_or_edit_category(category_id, t))

@router.callback_query(F.data.startswith('admin_category_filter:'))
@admin_only
async def admin_products_by_category(callback: CallbackQuery, state: FSMContext, t):
    """
    Displays products from the selected category (admin filter).
	"""
    category_id = int(callback.data.split(':', 1)[1])
    page = 1
    category = await Category.get(id=category_id)
    text = t('admin_catalog.misc.b-tovary-kategorii-b').format(name=category.name)
    func = get_products_page_by_category(category_id, page)
    await get_products_info(callback, t, page, text, func, state)
    await callback.answer()
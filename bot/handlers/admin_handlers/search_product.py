from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from .admin_access import admin_only
from database.models import Product
from ...keyboards.admin.catalog_keyboards import product_admin_keyboard, show_products_for_search, \
    back_to_search_keyboard, back_menu
from ...states.admin_states.product_states import ProductSearchStates
from ...utils.common_utils import format_price, delete_request_and_user_message
router = Router()

@router.callback_query(F.data == 'admin_search_product')
@admin_only
async def start_search_product(callback: CallbackQuery, t, state: FSMContext, **_):
    """
    Starts the FSM for product search.
	"""
    msg = await callback.message.edit_text(t('search_product.messages.vvedite-nazvanie-tovara'), reply_markup=back_menu(t))
    await state.update_data(main_message_id=msg.message_id)
    await state.set_state(ProductSearchStates.waiting_query)
    await callback.answer()

@router.message(ProductSearchStates.waiting_query)
@admin_only
async def search_product_query(message: Message, t, state: FSMContext, **_):
    """
    Searches for a product by the entered text or ID.
	"""
    await delete_request_and_user_message(message, state)
    query = message.text.strip()
    if query.isdigit():
        products = await Product.filter(id=int(query)).all()
    else:
        products = await Product.filter(name__icontains=query).all()
    if not products:
        msg = await message.answer(t('search_product.messages.nichego-ne-najdeno-poprobujte'), reply_markup=back_to_search_keyboard(t))
        await state.update_data(main_message_id=msg.message_id)
        await state.clear()
        return
    if len(products) == 1:
        product = products[0]
        await product.fetch_related('category')
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
            await message.bot.send_photo(chat_id=message.chat.id, photo=product.photo, caption=text, reply_markup=await product_admin_keyboard(product.id, t))
        else:
            msg = await message.answer(text, reply_markup=await product_admin_keyboard(product.id, t))
            await state.update_data(main_message_id=msg.message_id)
        await state.clear()
    else:
        await message.answer(t("search_order.naydeno-tovarov").format(products=len(products)), reply_markup=show_products_for_search(products, t))
        await state.clear()
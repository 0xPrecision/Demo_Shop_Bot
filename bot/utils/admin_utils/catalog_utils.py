from collections.abc import Awaitable
from typing import Union, Tuple, List

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.admin.catalog_keyboards import products_list_keyboard, admin_categories_keyboard, \
    ask_of_create_product, ask_of_create_category, change_category_keyboard
from bot.utils.common_utils import format_price, delete_request_and_user_message
from database.crud import get_all_categories
from database.models import Product


# ========== PRODUCTS_UTILS ==========

def get_product_short_info(product) -> str:
    """
    Generates a short string with the main product info for an inline keyboard.
    
    :param product: Product object.
    :return: String like "Name | Price ₽".
	"""
    return f"{product.name} | {format_price(product.price)} ₽"


async def get_products_info(callback: CallbackQuery, page: int, text: str, func: Awaitable[Tuple[List["Product"], bool, bool]], state: FSMContext) -> None:
    """
    Generic asynchronous handler for displaying a paginated product list.
    
    :param callback: CallbackQuery from aiogram.
    :param page: Current page number.
    :param text: Message text.
    :param func: Awaitable returning a tuple (products, has_next, has_prev).
    :param state: FSMContext from aiogram.
    :return: None.
	"""
    await delete_request_and_user_message(callback.message, state)
    products, has_next, has_prev = await func
    products_for_kb = [
        (product.id, get_product_short_info(product)) for product in products
    ]
    if not products:
        msg = await callback.message.answer(
            "Товаров пока нет.\n\n"
            "Хотите создать первый товар?",
            reply_markup=ask_of_create_product()
        )
        await state.update_data(main_message_id=msg.message_id)
        return

    msg = await callback.message.answer(
        text=text,
        reply_markup=products_list_keyboard(products_for_kb, page, has_next, has_prev)
    )

    await state.update_data(main_message_id=msg.message_id)


async def filter_or_change_pr_category(
        event: Union[CallbackQuery, Message],
        state: FSMContext,
        text: str = None,
        product_id: int = None
    ) -> None:
        """
        Generic handler for displaying the list of categories:
        — filter products by category
        — or change the category for a specific product (if product_id is provided).
        Works with CallbackQuery and Message.
        
        :param event: CallbackQuery or Message from aiogram.
        :param text: Message text.
        :param state: User's FSMContext.
        :param product_id: Product ID if category change is required (optional).
        :return: None.
	"""
        categories = await get_all_categories()
        if not categories:
            msg_text = "Категории не найдены.\n\nХотите создать новую?"
            kb = ask_of_create_category()
            if isinstance(event, CallbackQuery):
                await event.message.edit_text(msg_text, reply_markup=kb)
                await event.answer()
            else:  # Message
                msg = await event.answer(msg_text, reply_markup=kb)
                await state.update_data(main_message_id=msg.message_id)
            return

        if product_id:
            await state.update_data(edit_product_id=product_id)

        cur_state = await state.get_state()
        kb = change_category_keyboard(categories) if cur_state else admin_categories_keyboard(categories)
        msg_text = text or "Выберите категорию:"

        if isinstance(event, CallbackQuery):
            await event.message.edit_text(msg_text, reply_markup=kb)
            await event.answer()
        else:  # Message
            msg = await event.answer(msg_text, reply_markup=kb)
            await state.update_data(main_message_id=msg.message_id)

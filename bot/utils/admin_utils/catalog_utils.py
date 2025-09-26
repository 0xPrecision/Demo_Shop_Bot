from collections.abc import Awaitable
from typing import List, Tuple, Union

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.admin.catalog_keyboards import (
    admin_categories_keyboard,
    ask_of_create_category,
    ask_of_create_product,
    change_category_keyboard,
    products_list_keyboard,
)
from bot.utils.common_utils import delete_request_and_user_message, format_price
from database.crud import get_all_categories
from database.models import Product


def get_product_short_info(product, t) -> str:
    """
    Generates a short string with the main product info for an inline keyboard.

    :param product: Product object.
    :return: String like "Name | Price".
    """
    return f'{product.name} | {format_price(product.price)} {t("currency")}'


async def get_products_info(
    callback: CallbackQuery,
    t,
    page: int,
    text: str,
    func: Awaitable[Tuple[List["Product"], bool, bool]],
    state: FSMContext,
    **_,
) -> None:
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
        (product.id, get_product_short_info(product, t)) for product in products
    ]
    if not products:
        msg = await callback.message.answer(
            t("catalog_utils.messages.tovarov-poka-net-hotite"),
            reply_markup=ask_of_create_product(t),
        )
        await state.update_data(main_message_id=msg.message_id)
        return
    msg = await callback.message.answer(
        text=text,
        reply_markup=products_list_keyboard(
            products_for_kb, page, has_next, has_prev, t
        ),
    )
    await state.update_data(main_message_id=msg.message_id)


async def filter_or_change_pr_category(
    event: Union[CallbackQuery, Message],
    state: FSMContext,
    t,
    text: str = None,
    product_id: int = None,
    **_,
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
        msg_text = t("kategorii-ne-naydeny")
        kb = ask_of_create_category(t, **_)
        if isinstance(event, CallbackQuery):
            await event.message.edit_text(msg_text, reply_markup=kb)
            await event.answer()
        else:
            msg = await event.answer(msg_text, reply_markup=kb)
            await state.update_data(main_message_id=msg.message_id)
        return
    if product_id:
        await state.update_data(edit_product_id=product_id)
    cur_state = await state.get_state()
    kb = (
        change_category_keyboard(categories)
        if cur_state
        else admin_categories_keyboard(categories, t, **_)
    )
    msg_text = text or t("user_catalog.messages.vyberite-kategoriyu")
    if isinstance(event, CallbackQuery):
        await event.message.edit_text(msg_text, reply_markup=kb)
        await event.answer()
    else:
        msg = await event.answer(msg_text, reply_markup=kb)
        await state.update_data(main_message_id=msg.message_id)

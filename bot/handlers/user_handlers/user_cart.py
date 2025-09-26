import asyncio

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.keyboards.user.user_common_keyboards import cart_back_menu
from bot.keyboards.user.user_main_menu import main_menu
from bot.utils.common_utils import delete_request_and_user_message
from bot.utils.user_utils.user_cart_utils import build_cart_view
from config_data.bot_instance import bot
from database.crud import (
    add_to_cart,
    clear_cart,
    get_all_products,
    get_cart,
    remove_from_cart,
)

router = Router()


async def show_cart(callback: CallbackQuery, state: FSMContext, t, **_) -> None:
    """
    Displays the user's cart.
    """
    await delete_request_and_user_message(callback.message, state)
    user_id = callback.from_user.id
    cart_items = await get_cart(user_id)
    if cart_items:
        text, keyboard = await build_cart_view(cart_items, t, page=0)
        await callback.bot.send_message(
            user_id, text, reply_markup=keyboard or main_menu(t)
        )
    else:
        await bot.send_message(
            user_id,
            t("user_cart.messages.vasha-korzina-pusta"),
            reply_markup=cart_back_menu(t),
        )


@router.callback_query(F.data.startswith("cart_"))
async def paginate_cart(callback: CallbackQuery, t) -> None:
    """
    Handles cart pagination.

    :param callback: User's CallbackQuery.
    :return: None
    """
    page = int(callback.data.split("_")[1]) if "_" in callback.data else 0
    cart_items = await get_cart(callback.from_user.id)
    text, keyboard = await build_cart_view(cart_items, t, page)
    try:
        await callback.message.edit_text(text, reply_markup=keyboard or main_menu(t))
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            pass
        else:
            raise
    await callback.answer()


@router.callback_query(F.data.startswith("addtocart_"))
async def add_to_cart_handler(callback: CallbackQuery, t, **_) -> None:
    """
    Handler for the 'Add to cart' button: adds a product to the user's cart.

    :param callback: User's CallbackQuery.
    :return: None
    """
    user_id = callback.from_user.id
    product_id = int(callback.data.split("_")[1])
    products = await get_all_products()
    product = next((p for p in products if p.id == product_id), None)
    if not product:
        await callback.answer(t("user_cart.messages.tovar-ne-najden"), show_alert=True)
        return
    await add_to_cart(user_id, product_id, 1)
    sent_message = await bot.send_message(
        user_id, t("user_cart.messages.tovar-dobavlen-v-korzinu")
    )
    await asyncio.sleep(1)
    await bot.delete_message(user_id, sent_message.message_id)


@router.callback_query(F.data.startswith("removefromcart_"))
async def remove_from_cart_handler(callback: CallbackQuery, t, **_) -> None:
    """
    Handler for the 'Remove from cart' button: removes a product from the user's cart.

    :param callback: User's CallbackQuery.
    :return: None
    """
    user_id = callback.from_user.id
    parts = callback.data.split("_")
    product_id = int(parts[1])
    page = int(parts[2]) if len(parts) > 2 else 0
    await remove_from_cart(user_id, product_id)
    cart_items = await get_cart(user_id)
    text, keyboard = await build_cart_view(cart_items, t, page)
    try:
        await callback.message.edit_text(text, reply_markup=keyboard)
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            pass
        else:
            raise
    sent_message = await bot.send_message(
        user_id, t("user_cart.messages.tovar-udalen-iz-korziny")
    )
    await asyncio.sleep(1)
    await bot.delete_message(user_id, sent_message.message_id)


@router.callback_query(F.data == "clear_cart")
async def clear_cart_handler(
    callback: CallbackQuery, t, state: FSMContext, **_
) -> None:
    """
    Handler for the 'Clear cart' button: clears the user's cart.
    """
    user_id = callback.from_user.id
    await clear_cart(user_id)
    await delete_request_and_user_message(callback.message, state)
    await bot.send_message(
        user_id,
        t("user_cart.messages.vasha-korzina-pusta"),
        reply_markup=cart_back_menu(t),
    )

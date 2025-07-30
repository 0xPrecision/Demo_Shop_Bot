import asyncio
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from database.crud import get_cart, add_to_cart, remove_from_cart, clear_cart, get_all_products
from bot.utils.user_utils.user_cart_utils import build_cart_view
from bot.utils.common_utils import delete_request_and_user_message
from bot.keyboards.user.user_main_menu import main_menu
from bot.keyboards.user.user_common_keyboards import cart_back_menu
from config_data.bot_instance import bot

router = Router()

async def show_cart(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Показывает пользователю его корзину.
    """
    await delete_request_and_user_message(callback.message, state)
    user_id = callback.from_user.id
    cart_items = await get_cart(user_id)
    if cart_items:
        text, keyboard = await build_cart_view(cart_items, page=0)
        await callback.bot.send_message(user_id, text, reply_markup=keyboard or main_menu())
    else:
        await bot.send_message(user_id, "🧹 Ваша корзина пуста.", reply_markup=cart_back_menu())

@router.callback_query(F.data.startswith("cart_"))
async def paginate_cart(callback: CallbackQuery) -> None:
    """
    Обработка пагинации корзины.

    :param callback: CallbackQuery от пользователя.
    :return: None
    """
    page = int(callback.data.split("_")[1]) if "_" in callback.data else 0
    cart_items = await get_cart(callback.from_user.id)
    text, keyboard = await build_cart_view(cart_items, page)
    try:
        await callback.message.edit_text(text, reply_markup=keyboard or main_menu())
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            pass
        else:
            raise
    await callback.answer()

@router.callback_query(F.data.startswith("addtocart_"))
async def add_to_cart_handler(callback: CallbackQuery) -> None:
    """
    Обработчик кнопки 'В корзину': добавляет товар в корзину пользователя.

    :param callback: CallbackQuery от пользователя.
    :return: None
    """
    user_id = callback.from_user.id
    product_id = int(callback.data.split("_")[1])

    # Получаем товар по id
    products = await get_all_products()
    product = next((p for p in products if p.id == product_id), None)
    if not product:
        await callback.answer("Товар не найден!", show_alert=True)
        return

    await add_to_cart(user_id, product_id, 1)
    sent_message = await bot.send_message(user_id, "Товар добавлен в корзину!")
    await asyncio.sleep(1)
    await bot.delete_message(user_id, sent_message.message_id)

@router.callback_query(F.data.startswith("removefromcart_"))
async def remove_from_cart_handler(callback: CallbackQuery) -> None:
    """
    Обработчик кнопки 'Убрать из корзины': удаляет товар из корзины пользователя.

    :param callback: CallbackQuery от пользователя.
    :return: None
    """
    user_id = callback.from_user.id
    parts = callback.data.split("_")
    product_id = int(parts[1])
    page = int(parts[2]) if len(parts) > 2 else 0

    await remove_from_cart(user_id, product_id)
    cart_items = await get_cart(user_id)
    text, keyboard = await build_cart_view(cart_items, page)
    try:
        await callback.message.edit_text(text, reply_markup=keyboard)
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            pass
        else:
            raise

    sent_message = await bot.send_message(user_id, "Товар удалён из корзины!")
    await asyncio.sleep(1)
    await bot.delete_message(user_id, sent_message.message_id)

@router.callback_query(F.data == "clear_cart")
async def clear_cart_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обработчик кнопки 'Очистить корзину': очищает корзину пользователя.
    """
    user_id = callback.from_user.id
    await clear_cart(user_id)
    await delete_request_and_user_message(callback.message, state)
    await bot.send_message(user_id, "🧹 Ваша корзина пуста.", reply_markup=cart_back_menu())


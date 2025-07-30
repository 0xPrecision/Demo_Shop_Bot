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
    Генерирует короткую строку с основной информацией о товаре для инлайн-клавиатуры.

    :param product: Объект товара (Product).
    :return: Строка вида "Название | Цена ₽".
    """
    return f"{product.name} | {format_price(product.price)} ₽"


async def get_products_info(callback: CallbackQuery, page: int, text: str, func: Awaitable[Tuple[List["Product"], bool, bool]], state: FSMContext) -> None:
    """
    Универсальный асинхронный обработчик для вывода списка товаров с пагинацией.

    :param callback: CallbackQuery из aiogram.
    :param page: Номер текущей страницы.
    :param text: Текст для сообщения.
    :param func: Awaitable, возвращающий кортеж (products, has_next, has_prev).
    :param state: FSMContext из aiogram.
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
        Универсальный обработчик для показа списка категорий:
        — фильтрация товаров по категории
        — или смена категории для конкретного товара (если указан product_id).
        Работает с CallbackQuery и Message.

        :param event: CallbackQuery или Message из aiogram.
        :param text: Текст для сообщения.
        :param state: FSMContext пользователя.
        :param product_id: ID товара, если требуется сменить категорию (опционально).
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

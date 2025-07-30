from decimal import Decimal
from typing import List, Tuple

from aiogram.fsm.context import FSMContext
from aiogram.types import Message


def paginate(items: List, page: int, page_size: int) -> Tuple[List, int, int]:
    """
    Универсальная пагинация для любого списка.

    :param items: Список элементов (например, товаров)
    :param page: Номер текущей страницы (от 0)
    :param page_size: Количество элементов на страницу
    :return: (Список элементов на текущей странице, всего страниц, номер текущей страницы)
    """
    total = len(items)
    total_pages = (total + page_size - 1) // page_size
    start = page * page_size
    end = start + page_size
    items_on_page = items[start:end]
    return items_on_page, total_pages, page


def format_product_name(name: str, max_len: int = 20) -> str:
    """Обрезает название для кнопки, если слишком длинное."""
    return name if len(name) <= max_len else name[:max_len - 3] + "..."

def format_price(price) -> str:
    return f"{Decimal(price):,.0f}".replace(",", " ")


async def delete_request_and_user_message(
    message: Message,
    state: FSMContext,
    data: dict = None
) -> None:
    """
    Удаляет предыдущее предупреждение (main_message_id) и сообщение пользователя.

    :param message: Объект Message пользователя.
    :param state: FSMContext.
    :param data: dict с данными FSM (если не передан — будет получен внутри).
    """
    if data is None:
        data = await state.get_data()
    main_message_id = data.get('main_message_id')
    if main_message_id:
        try:
            await message.bot.delete_message(message.chat.id, main_message_id)
        except Exception:
            pass
        await state.update_data(main_message_id=None)
    try:
        await message.delete()
    except Exception:
        pass
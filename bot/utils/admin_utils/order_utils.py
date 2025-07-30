from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.keyboards.admin.order_keyboards import orders_list_keyboard, change_order_status
from bot.utils.common_utils import format_price
from database.crud import get_orders_page, get_order_items
from database.models import Order


def get_order_short_info(order) -> str:
    """
    Генерирует короткое описание заказа для отображения в инлайн-клавиатуре.
    """
    date = order.created_at.strftime("%d.%m %H:%M")
    return f"{date} | {order.status} | {format_price(order.total_price)} ₽"


async def show_orders(callback: CallbackQuery, page: int, text: str):
    """
    Выводит список заказов с пагинацией и инлайн-клавиатурой.

    :param callback: CallbackQuery — объект события Telegram.
    :param page: int — номер текущей страницы (от 1).
    :param text: str — заголовок или текст сообщения.
    :return: None
    """
    orders, has_next, has_prev = await get_orders_page(page)
    orders_for_kb = [
        (order.id, get_order_short_info(order)) for order in orders
    ]
    if not orders:
        await callback.answer("Заказов пока нет.", show_alert=True)
        return
    await callback.message.edit_text(
        text,
        reply_markup=orders_list_keyboard(orders_for_kb, page, has_next, has_prev)
    )


async def admin_show_order_summary(event, state: FSMContext, order: Order, order_id: int):
    """
    Универсально отправляет администратору подробное описание заказа,
    включая все позиции, стоимость и данные клиента.
    :param event: CallbackQuery или Message — объект события Telegram.
    :param state: FSMContext
    :param order: Order — объект заказа.
    :param order_id: int — идентификатор заказа.
    :return: None
    """
    await order.fetch_related('user')
    order_items = await get_order_items(order)
    order_info = (
        f"ФИО клиента: {order.name}\n"
        f"Номер телефона: {order.phone}\n"
        f"Дата: {order.created_at.strftime('%d.%m.%Y %H:%M')}\n"
        f"Состав:\n\n"
    )
    for item in order_items:
        price = item.price_at_order * item.quantity
        order_info += f"— <i>{item.product.name}</i> × {item.quantity} = {format_price(price)} ₽\n"

    order_info += (
        f"\nСтоимость: {format_price(order.total_price)} ₽\n"
        f"Способ оплаты: {order.payment_method}\n"
        f"Доставка: {order.delivery_method}\n"
        f"Адрес доставки: {order.address}\n"
        f"Комментарий: {order.comment}"
    )

    text = (
        f"📝 <b>Детали заказа #{order_id}</b>\n\n"
        f"{order_info}"
    )

    # Универсально отправляет сообщение (edit_text для callback, answer для message)
    if hasattr(event, "message"):  # CallbackQuery
        await event.message.edit_text(
            text=text,
            reply_markup=change_order_status()
        )
    else:  # Message
        msg = await event.answer(
            text=text,
            reply_markup=change_order_status()
        )
        await state.update_data(main_message_id=msg.message_id)

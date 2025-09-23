from typing import Dict, Optional
from decimal import Decimal
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from bot.states.user_states.order_states import OrderStates
from bot.keyboards.user.order_keyboards import order_details_keyboard, order_confirm_keyboard, show_orders_keyboard
from bot.keyboards.user.user_main_menu import main_menu
from bot.utils.common_utils import delete_request_and_user_message
from bot.utils.common_utils import format_price, format_product_name
from database.crud import get_order_by_id, get_order_items, get_cart, get_orders

async def show_orders_menu(callback: CallbackQuery, state: FSMContext, msg_text: str, order_status: Optional[str]=None) -> None:
    """
    Displays the user's orders menu with optional status filter.
    
    :param callback: User's CallbackQuery object.
    :param msg_text: Message if no orders exist.
    :param order_status: Optional order status filter.
	"""
    await delete_request_and_user_message(callback.message, state)
    user_id = callback.from_user.id
    orders = await get_orders(user_id)
    if not orders:
        await callback.message.answer(msg_text, reply_markup=main_menu())
        return
    text = f"🧾 Ваши заказы:\n{'-' * 19}\n\n"
    filtered_orders = [order for order in orders if order.status == order_status] if order_status else orders
    if not filtered_orders:
        text += '\nНет заказов с выбранным статусом.'
    else:
        filtered_orders = sorted(filtered_orders, key=lambda x: x.created_at, reverse=True)
        for order in filtered_orders:
            text += f'📝 <b>#{order.id}</b> | 📅 <i>{order.created_at:%d.%m.%Y}</i> | {order.status} | 💰 <b>{format_price(order.total_price)} ₽</b>\n'
    text += f"\n\n{'-' * 19}\n<i>Нажмите на заказ, чтобы узнать детали</i>"
    await callback.message.answer(text, reply_markup=show_orders_keyboard(orders))

async def get_order_details(order_id: int, t, **_) -> Dict:
    """
    Get detailed order information by its identifier.
    
    :param order_id: int — order ID.
    :return: Dict — {"text": description, "keyboard": inline keyboard}.
	"""
    order = await get_order_by_id(order_id)
    if not order:
        return {'text': t('admin_orders.messages.zakaz-ne-najden'), 'keyboard': order_details_keyboard(order_id)}
    order_items = await get_order_items(order)
    total = sum([item.quantity * float(item.product.price) for item in order_items])
    items_text = '\n'.join([f'• {format_product_name(item.product.name)} — {item.quantity} x {format_price(item.product.price)} ₽ = {format_price(item.quantity * float(item.product.price))} ₽' for item in order_items])
    text = f"🧾 <b>Заказ #{order.id}</b>\n📅 <b>Дата:</b> {order.created_at:%d.%m.%Y}\n📦 <b>Статус:</b> <b>{order.status}</b>\n💳 <b>Оплата:</b> {order.payment_method or '-'}\n🚚 <b>Доставка:</b> {order.delivery_method or '-'}\n🏠 <b>Адрес:</b> {order.address or '-'}\n\n<b>Товары:</b>\n{items_text}\n\n<b>Итого: {format_price(total)} ₽</b>"
    return {'text': text, 'keyboard': order_details_keyboard(order.id)}

async def show_order_summary(message_or_callback, state: FSMContext) -> None:
    """
    Displays the order summary to the user with all entered data (supports Cart ORM and dict).
    Provides options to confirm the order or edit the data.
	"""
    await delete_request_and_user_message(message_or_callback, state)
    user_id = message_or_callback.from_user.id
    data = await state.get_data()
    summary = f"Проверьте данные заказа:\n\nИмя: {data.get('name', '-')}\nТелефон: {data.get('phone', '-')}\n{data.get('delivery_method', '-')}\nАдрес доставки: {data.get('address', 'Не указан')}\nКомментарий: {data.get('comment', '-')}\n\nОплата: {data.get('payment_method', '-')}\n\nВаш заказ:\n"
    total = 0
    cart_items = await get_cart(user_id)
    for item in cart_items:
        name = format_product_name(item.product.name)
        qty = item.quantity
        price = Decimal(item.product.price)
        pr_sum = price * qty
        total += pr_sum
        summary += f'{name} - x{qty} ({format_price(pr_sum)} ₽)\n'
    summary += f'\nОбщая сумма заказа: <b>{format_price(total)} ₽</b>\n\nПеред отправкой вы можете изменить любой пункт.'
    if hasattr(message_or_callback, 'edit_text'):
        await message_or_callback.answer(summary, reply_markup=order_confirm_keyboard())
    else:
        await message_or_callback.message.answer(summary, reply_markup=order_confirm_keyboard())
    await state.set_state(OrderStates.confirm)
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Tuple

from bot.constants import ORDER_STATUSES


def orders_list_keyboard(orders: List[Tuple[int, str]], page: int = 1, has_next: bool = False, has_prev: bool = False) -> InlineKeyboardMarkup:
    """
    Keyboard for the orders list.
    :param orders: list of (order_id, short_info)
    :param page: current page
    :param has_next: whether there is a next page
    :param has_prev: whether there is a previous page
    :return: InlineKeyboardMarkup
	"""
    buttons = [
        [InlineKeyboardButton(text=f"#_id {order_id} | {short_info}", callback_data=f"admin_order_detail:{order_id}")]
        for order_id, short_info in orders
    ]
    nav = []
    if has_prev:
        nav.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"admin_orders_page:{page-1}"))
    if has_next:
        nav.append(InlineKeyboardButton(text="Вперёд ➡️", callback_data=f"admin_orders_page:{page+1}"))
    if nav:
        buttons.append(nav)
    buttons.append([InlineKeyboardButton(text="🔍 Поиск заказа", callback_data="admin_search_order")])
    buttons.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="/start_admin")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def show_orders_for_search(orders) -> InlineKeyboardMarkup:
    """
    Creates an inline keyboard for searching and selecting an order from the list.
    
    :param orders: list of orders (Order), each must have attributes id, user.full_name, total_price.
    :return: InlineKeyboardMarkup — keyboard for displaying found orders.
	"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=f"id#{o.id} | {o.user.full_name} | {o.total_price}₽",
                callback_data=f"admin_order_detail:{o.id}"
            )] for o in orders
        ]
    )


def change_order_status():
    """
    Keyboard for changing order status and contacting the customer.
	"""
    return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="⚡️ Сменить статус", callback_data="change_status")],
                [InlineKeyboardButton(text="🏠 Главное меню", callback_data="/start_admin")]
            ]
        )


def status_keyboard(order_id: int, current_status: str) -> InlineKeyboardMarkup:
    """
    Keyboard for changing the order status.
    :param order_id: Order ID.
    :param current_status: Current order status.
    :return: InlineKeyboardMarkup
	"""
    buttons = []
    for status_code, status_label in ORDER_STATUSES:
        if status_code == current_status:
            continue
        buttons.append(
            [InlineKeyboardButton(
                text=status_label,
                callback_data=f"admin_order_set_status:{order_id}:{status_code}"
            )]
        )
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=f"admin_order_detail:{order_id}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)




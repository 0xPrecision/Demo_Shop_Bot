from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Optional
from database.models import Order


def format_status(status: str) -> str:
    """
    Adds an emoji to the status.
	"""
    mapping = {
        "В работе": "🟡 В работе",
        "Готово": "🟢 Завершён",
        "Отменён": "🔴 Отменён"
    }
    return mapping.get(status, status)

def show_orders_keyboard(orders: List[Order]) -> InlineKeyboardMarkup:
    """
    Creates an inline keyboard for the user's orders list.
    
    Each order line gets its own button to view details.
    At the bottom — a button to return to the main menu.
    
    :param orders: List of the user's Order objects.
    :return: InlineKeyboardMarkup — inline keyboard.
	"""
    keyboard = [
        [
            InlineKeyboardButton(
                text=f"📝 Заказ #{order.id} — {format_status(order.status)}",
                callback_data=f"order_details_{order.id}"
            )
        ]
        for order in orders
    ]

    keyboard.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data="my_orders")
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def order_details_keyboard(order_id: Optional[int] = None) -> InlineKeyboardMarkup:
    """
    Создаёт клавиатуру для подробного просмотра заказа.
    
    Кнопки: возврат к списку заказов и переход в главное меню.
    
    :param order_id: идентификатор заказа (не используется, но можно для расширения).
    :return: InlineKeyboardMarkup — инлайн-клавиатура.
	"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ К списку заказов", callback_data="menu_orders")],
        [InlineKeyboardButton(text="🏠 В главное меню", callback_data="menu_main")]
    ])


def order_confirm_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Оформить заказ", callback_data="confirm_order")],
            [InlineKeyboardButton(text="⬅️ Вернуться в каталог", callback_data="menu_catalog")],
            [InlineKeyboardButton(text="✏️ Редактировать данные", callback_data="edit_data")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_order")]
        ]
    )

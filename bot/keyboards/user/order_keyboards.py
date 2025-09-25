from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Optional

from bot.utils.common_utils import get_order_status_label
from database.models import Order


def show_orders_keyboard(orders: List[Order], t, **_) -> InlineKeyboardMarkup:
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
                text=t("orders.list.item").format(
                    order_id=order.id,
                    status=get_order_status_label(order.status, t)  # тут возвращается локализованный текст со смайликом
                ),
                callback_data=f"order_details_{order.id}"
            )
        ]
        for order in orders
    ]
    keyboard.append([InlineKeyboardButton(text=t('catalog_keyboards.buttons.nazad'), callback_data='my_orders')])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def order_details_keyboard(t, order_id: Optional[int] = None, **_) -> InlineKeyboardMarkup:
    """
    Creates a keyboard for detailed order view.

    Buttons: return to the list of orders and go to the main menu.

    :param order_id: order identifier (not used, but can be kept for extension).
    :return: InlineKeyboardMarkup — inline keyboard.
    """
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t('order_keyboards.buttons.k-spisku-zakazov'), callback_data='menu_orders')], [InlineKeyboardButton(text=t('order_keyboards.buttons.v-glavnoe-menyu'), callback_data='menu_main')]])

def order_confirm_keyboard(t, **_):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t('order_keyboards.buttons.oformit-zakaz'), callback_data='confirm_order')], [InlineKeyboardButton(text=t('order_keyboards.buttons.vernutsya-v-katalog'), callback_data='menu_catalog')], [InlineKeyboardButton(text=t('order_keyboards.buttons.redaktirovat-dannye'), callback_data='edit_data')], [InlineKeyboardButton(text=t('catalog_keyboards.buttons.otmena'), callback_data='cancel_order')]])
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.utils.common_utils import format_product_name


def cart_keyboard(products: list[tuple], page: int, total_pages: int) -> InlineKeyboardMarkup:
    """
    Creates an inline keyboard for the cart with navigation and a “Pay” button.
    :param products: List of (Cart, Product) tuples for the current page.
    :param page: Current page (from 0).
    :param total_pages: Total number of pages.
	"""
    keyboard = [
        [
            InlineKeyboardButton(
                text=f"{format_product_name(product.name)}",
                callback_data=f"product_{product.id}_cart"
            ),
            InlineKeyboardButton(
                text="Убрать из корзины",
                callback_data=f"removefromcart_{product.id}_{page}"
            ),
        ]
        for item, product in products
    ]

    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton(
            text="⬅️",
            callback_data=f"cart_{page-1}"
        ))

        nav_row.append(InlineKeyboardButton(
            text=f"Страница {page + 1}/{total_pages}", callback_data="noop"
        ))

    if page < total_pages - 1:
        nav_row.append(InlineKeyboardButton(
            text="➡️",
            callback_data=f"cart_{page+1}"
        ))
    if nav_row:
        keyboard.append(nav_row)

    keyboard.append([
        InlineKeyboardButton(text="✅ Оформить заказ", callback_data="place_an_order")
    ])


    keyboard.append([
        InlineKeyboardButton(text="🧹 Очистить корзину", callback_data="clear_cart")
    ])

    keyboard.append([
        InlineKeyboardButton(text="⬅️ В каталог", callback_data="menu_catalog")
    ])

    keyboard.append([
        InlineKeyboardButton(text="🏠 В главное меню", callback_data="menu_main")
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
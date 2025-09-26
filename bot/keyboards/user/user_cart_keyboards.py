from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.utils.common_utils import format_product_name


def cart_keyboard(
    products: list[tuple], page: int, total_pages: int, t, **_
) -> InlineKeyboardMarkup:
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
                callback_data=f"product_{product.id}_cart",
            ),
            InlineKeyboardButton(
                text=t("user_cart_keyboards.buttons.ubrat-iz-korziny"),
                callback_data=f"removefromcart_{product.id}_{page}",
            ),
        ]
        for item, product in products
    ]
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton(text="⬅️", callback_data=f"cart_{page - 1}"))
        nav_row.append(
            InlineKeyboardButton(
                text=t("user_catalog.page_label").format(
                    page=page, total_pages=total_pages
                ),
                callback_data="noop",
            )
        )
    if page < total_pages - 1:
        nav_row.append(InlineKeyboardButton(text="➡️", callback_data=f"cart_{page + 1}"))
    if nav_row:
        keyboard.append(nav_row)
    keyboard.append(
        [
            InlineKeyboardButton(
                text=t("order_keyboards.buttons.oformit-zakaz"),
                callback_data="place_an_order",
            )
        ]
    )
    keyboard.append(
        [
            InlineKeyboardButton(
                text=t("user_cart_keyboards.buttons.ochistit-korzinu"),
                callback_data="clear_cart",
            )
        ]
    )
    keyboard.append(
        [
            InlineKeyboardButton(
                text=t("user_cart_keyboards.buttons.v-katalog"),
                callback_data="menu_catalog",
            )
        ]
    )
    keyboard.append(
        [
            InlineKeyboardButton(
                text=t("order_keyboards.buttons.v-glavnoe-menyu"),
                callback_data="menu_main",
            )
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

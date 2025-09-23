from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu() -> InlineKeyboardMarkup:
    """
    Inline main menu keyboard for the user (all buttons in a column).
	"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Каталог", callback_data="menu_catalog")],
        [InlineKeyboardButton(text="Корзина", callback_data="menu_cart")],
        [InlineKeyboardButton(text="Профиль", callback_data="menu_profile")],
        [InlineKeyboardButton(text="Помощь", callback_data="menu_help")],
    ])
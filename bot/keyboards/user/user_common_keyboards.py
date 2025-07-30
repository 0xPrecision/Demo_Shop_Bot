from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def cart_back_menu():
    return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ В каталог", callback_data="menu_catalog")],
                [InlineKeyboardButton(text="🏠 В главное меню",callback_data="menu_main")]
            ]
        )
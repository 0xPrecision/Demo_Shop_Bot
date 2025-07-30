from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def help_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🛒 Каталог", callback_data="admin_catalog")],
            [InlineKeyboardButton(text="📦 Заказы", callback_data="admin_orders")],
            [InlineKeyboardButton(text="➕ Добавить товар", callback_data="admin_add_product")],
            [InlineKeyboardButton(text="➕ Добавить категорию", callback_data="admin_add_category")],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="/start_admin")]
        ]
    )
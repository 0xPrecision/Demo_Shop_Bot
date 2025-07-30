from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def admin_main_menu():
    return InlineKeyboardMarkup(inline_keyboard = [
        [InlineKeyboardButton(text="Каталог", callback_data="admin_catalog")],
        [InlineKeyboardButton(text="Заказы", callback_data="admin_orders")],
        [InlineKeyboardButton(text="Выгрузить статистику", callback_data="admin_stats")],
        [InlineKeyboardButton(text="ℹ️ Помощь", callback_data="admin_help")]
    ])

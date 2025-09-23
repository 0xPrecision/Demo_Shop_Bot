from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def admin_main_menu(t, **_):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t('admin_menu.buttons.katalog'), callback_data='admin_catalog')], [InlineKeyboardButton(text=t('admin_menu.buttons.zakazy'), callback_data='admin_orders')], [InlineKeyboardButton(text=t('admin_menu.buttons.vygruzit-statistiku'), callback_data='admin_stats')], [InlineKeyboardButton(text=t('admin_menu.buttons.pomosch'), callback_data='admin_help')]])
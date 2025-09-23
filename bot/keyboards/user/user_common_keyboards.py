from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def cart_back_menu(t, **_):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t('user_cart_keyboards.buttons.v-katalog'), callback_data='menu_catalog')], [InlineKeyboardButton(text=t('order_keyboards.buttons.v-glavnoe-menyu'), callback_data='menu_main')]])
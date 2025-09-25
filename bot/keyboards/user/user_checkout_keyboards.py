from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def payment_methods_keyboard(t, **_):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t('user_checkout_keyboards.buttons.kartoj-onlajn'), callback_data='pay_card')], [InlineKeyboardButton(text=t('user_checkout_keyboards.buttons.nalichnye'), callback_data='pay_cash')], [InlineKeyboardButton(text=t('user_checkout_keyboards.buttons.yumoney'), callback_data='pay_yoomoney')], [InlineKeyboardButton(text=t('user_checkout_keyboards.buttons.nazad-v-katalog'), callback_data='menu_catalog')], [InlineKeyboardButton(text=t('order_keyboards.buttons.v-glavnoe-menyu'), callback_data='menu_main')]])

def delivery_methods_keyboard(t, **_):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t('user_checkout_keyboards.buttons.kurer'), callback_data='delivery_courier')], [InlineKeyboardButton(text=t('user_checkout_keyboards.buttons.samovyvoz'), callback_data='delivery_pickup')], [InlineKeyboardButton(text=t('user_checkout_keyboards.buttons.nazad-v-katalog'), callback_data='menu_catalog')], [InlineKeyboardButton(text=t('order_keyboards.buttons.v-glavnoe-menyu'), callback_data='menu_main')]])

def change_address_keyboard(t, **_):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t('user_checkout_keyboards.buttons.ispolzovat-adres-iz-profilya'), callback_data='use_profile_address')], [InlineKeyboardButton(text=t('user_checkout_keyboards.buttons.vvesti-novyj-adres'), callback_data='enter_new_address')]])

def checkout_edit_keyboard(t, **_):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t('user_profile_keyboards.buttons.fio'), callback_data='edit_name')], [InlineKeyboardButton(text=t('user_checkout_keyboards.buttons.telefon'), callback_data='edit_phone')], [InlineKeyboardButton(text=t('user_checkout_keyboards.buttons.adres'), callback_data='edit_address')], [InlineKeyboardButton(text=t('user_checkout_keyboards.buttons.kommentarij'), callback_data='edit_comment')], [InlineKeyboardButton(text=t('user_checkout_keyboards.buttons.sposob-oplaty'), callback_data='edit_payment')], [InlineKeyboardButton(text=t('user_checkout_keyboards.buttons.sposob-dostavki'), callback_data='edit_delivery')], [InlineKeyboardButton(text=t('catalog_keyboards.buttons.nazad'), callback_data='back_to_confirm')]])

def profile_data_confirm_keyboard(t, **_):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t('user_checkout_keyboards.buttons.da-ispolzovat-profil'), callback_data='use_profile')], [InlineKeyboardButton(text=t('user_checkout_keyboards.buttons.zapolnit-zanovo'), callback_data='fill_manually')], [InlineKeyboardButton(text=t('catalog_keyboards.buttons.otmena'), callback_data='cancel_order')]])
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def create_profile(t, **_):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t('user_profile_keyboards.buttons.sozdat-profil'), callback_data='create_profile')], [InlineKeyboardButton(text=t('user_profile_keyboards.buttons.v-menyu-profilya'), callback_data='menu_profile')]])

def profile_confirm_or_edit_keyboard(t, **_):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t('catalog_keyboards.buttons.podtverdit'), callback_data='confirm_profile')], [InlineKeyboardButton(text=t('user_profile_keyboards.buttons.izmenit-dannye'), callback_data='edit_profile')], [InlineKeyboardButton(text=t('user_profile_keyboards.buttons.v-menyu-profilya'), callback_data='menu_profile')]])

def edit_profile_keyboard(t, **_):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t('user_profile_keyboards.buttons.fio'), callback_data='edit_profile_name')], [InlineKeyboardButton(text=t('user_checkout_keyboards.buttons.telefon'), callback_data='edit_profile_phone')], [InlineKeyboardButton(text=t('user_checkout_keyboards.buttons.adres'), callback_data='edit_profile_address')], [InlineKeyboardButton(text=t('user_profile_keyboards.buttons.v-menyu-profilya'), callback_data='menu_profile')]])

def profile_menu_keyboard(t, **_):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t('user_profile_keyboards.buttons.moi-dannye'), callback_data='my_data')], [InlineKeyboardButton(text=t('user_profile_keyboards.buttons.moi-zakazy'), callback_data='my_orders')], [InlineKeyboardButton(text=t('order_keyboards.buttons.v-glavnoe-menyu'), callback_data='menu_main')]])

def profile_orders_keyboard(t, **_):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t('user_profile_keyboards.buttons.tekuschie-zakazy'), callback_data='active_orders')], [InlineKeyboardButton(text=t('user_profile_keyboards.buttons.istoriya-zakazov'), callback_data='menu_orders')], [InlineKeyboardButton(text=t('user_profile_keyboards.buttons.v-menyu-profilya'), callback_data='menu_profile')]])
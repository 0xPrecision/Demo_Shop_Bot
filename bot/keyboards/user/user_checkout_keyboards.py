from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def payment_methods_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Картой онлайн", callback_data="pay_card")],
            [InlineKeyboardButton(text="Наличные", callback_data="pay_cash")],
            [InlineKeyboardButton(text="ЮMoney", callback_data="pay_yoomoney")],
            [InlineKeyboardButton(text="⬅️ Назад в каталог", callback_data="menu_catalog")],
            [InlineKeyboardButton(text="🏠 В главное меню", callback_data="menu_main")]
        ]
    )

def delivery_methods_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Курьер", callback_data="delivery_courier")],
            [InlineKeyboardButton(text="Самовывоз", callback_data="delivery_pickup")],
            [InlineKeyboardButton(text="⬅️ Назад в каталог", callback_data="menu_catalog")],
            [InlineKeyboardButton(text="🏠 В главное меню", callback_data="menu_main")]
        ]
    )


def change_address_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Использовать адрес из профиля", callback_data="use_profile_address")],
            [InlineKeyboardButton(text="Ввести новый адрес", callback_data="enter_new_address")]
        ]
    )

def checkout_edit_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Имя", callback_data="edit_name")],
            [InlineKeyboardButton(text="Телефон", callback_data="edit_phone")],
            [InlineKeyboardButton(text="Адрес", callback_data="edit_address")],
            [InlineKeyboardButton(text="Комментарий", callback_data="edit_comment")],
            [InlineKeyboardButton(text="Способ оплаты", callback_data="edit_payment")],
            [InlineKeyboardButton(text="Способ доставки", callback_data="edit_delivery")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_confirm")]
        ]
    )

def profile_data_confirm_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Да, использовать профиль", callback_data="use_profile")],
            [InlineKeyboardButton(text="✏️ Заполнить заново", callback_data="fill_manually")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_order")]
        ]
    )
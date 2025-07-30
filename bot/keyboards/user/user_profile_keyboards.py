from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def create_profile():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👤➕ Создать профиль", callback_data="create_profile")],
            [InlineKeyboardButton(text="⬅️ В меню профиля", callback_data="menu_profile")]
        ]
    )

def profile_confirm_or_edit_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_profile")],
            [InlineKeyboardButton(text="✏️ Изменить данные", callback_data="edit_profile")],
            [InlineKeyboardButton(text="⬅️ В меню профиля", callback_data="menu_profile")]
        ]
    )


def edit_profile_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="ФИО", callback_data="edit_profile_name")],
            [InlineKeyboardButton(text="Телефон", callback_data="edit_profile_phone")],
            [InlineKeyboardButton(text="Адрес", callback_data="edit_profile_address")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="menu_profile")]
        ]
    )

def profile_menu_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🧑‍💼 Мои данные", callback_data="my_data")],
            [InlineKeyboardButton(text="📦 Мои заказы", callback_data="my_orders")],
            [InlineKeyboardButton(text="🏠 В главное меню", callback_data="menu_main")]
        ]
    )


def profile_orders_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🚚 Текущие заказы", callback_data="active_orders")],
            [InlineKeyboardButton(text="🕓 История заказов", callback_data="menu_orders")],
            [InlineKeyboardButton(text="⬅️ В меню профиля", callback_data="menu_profile")]
        ]
    )
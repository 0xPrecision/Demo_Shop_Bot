from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu(t, **_) -> InlineKeyboardMarkup:
    """
    Inline main menu keyboard for the user (all buttons in a column).
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("help_keyboard.buttons.katalog"),
                    callback_data="menu_catalog",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("user_catalog_keyboards.buttons.korzina"),
                    callback_data="menu_cart",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("user_main_menu.buttons.profil"),
                    callback_data="menu_profile",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("admin_menu.buttons.pomosch"), callback_data="menu_help"
                )
            ],
        ]
    )

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def stats_actions() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬇️ Выгрузить заказы (CSV)", callback_data="admin_export_orders_csv")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="/start_admin")]
        ]
    )
from aiogram import Router, F
from aiogram.types import CallbackQuery
from .admin_access import admin_only
from ...keyboards.admin.help_keyboard import help_keyboard

router = Router()

@router.callback_query(F.data == "admin_help")
@admin_only
async def admin_help(callback: CallbackQuery):
    """
    Отправляет справку по возможностям админ-панели и быстрые ссылки.
    """
    text = (
        "👑 <b>Админ-панель: помощь</b>\n\n"
        "<b>Основные возможности:</b>\n"
        "— <b>Каталог:</b> добавление/редактирование/скрытие категорий и товаров\n"
        "— Поиск товаров и заказов\n"
        "— Смена статуса заказа с уведомлением клиента в Telegram\n"
        "— Статистика и экспорт в CSV\n\n"
        "<b>Навигация:</b>\n"
        "Для выбора опции или возврата в главное меню используйте кнопку ниже."
    )
    await callback.message.edit_text(text, reply_markup=help_keyboard())
    await callback.answer()

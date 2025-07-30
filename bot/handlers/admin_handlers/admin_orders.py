from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from bot.keyboards.admin.order_keyboards import status_keyboard
from database.models import Order
from ...constants import ORDER_STATUSES
from ...utils.admin_utils.order_utils import show_orders, admin_show_order_summary
from database.crud import get_order_by_id
from .admin_access import admin_only


router = Router()


@router.callback_query(F.data == "admin_orders")
@admin_only
async def admin_orders_list(callback: CallbackQuery):
    """
    Показывает первую страницу списка заказов.
    """
    page = 1
    text = "📦 <b>Список заказов</b> (выбери заказ для просмотра):"
    await show_orders(callback, page, text)
    await callback.answer()


@router.callback_query(F.data.startswith("admin_orders_page:"))
@admin_only
async def admin_orders_page(callback: CallbackQuery):
    """
    Перелистывание страниц списка заказов.
    """
    page = int(callback.data.split(":")[1])
    text = f"📦 <b>Список заказов</b> (стр. {page}):"
    await show_orders(callback, page, text)
    await callback.answer()


@router.callback_query(F.data.startswith("admin_order_detail:"))
@admin_only
async def admin_order_detail(callback: CallbackQuery, state: FSMContext):
    """
    Показывает детали одного заказа.
    """
    order_id = int(callback.data.split(":")[1])
    order = await get_order_by_id(order_id)

    if not order:
        await callback.answer("Заказ не найден.", show_alert=True)
        return
    await admin_show_order_summary(callback, state, order, order_id)
    await callback.answer()


@router.callback_query(F.data == "change_status")
@admin_only
async def change_order_status_menu(callback: CallbackQuery):
    """
    Показывает клавиатуру со статусами заказа.
    :param callback: CallbackQuery от админа.
    """
    message = callback.message
    # Пример извлечения id заказа из текста сообщения
    order_id = int(message.text.split("#")[1].split()[0])
    order = await get_order_by_id(order_id)
    if not order:
        await callback.answer("Заказ не найден.", show_alert=True)
        return
    await message.edit_reply_markup(reply_markup=status_keyboard(order.id, order.status))
    await callback.answer()


@router.callback_query(F.data.startswith("admin_order_set_status:"))
@admin_only
async def set_order_status(callback: CallbackQuery, state: FSMContext):
    """
    Сохраняет выбранный статус заказа, уведомляет клиента, возвращает на детали заказа.
    """
    _, order_id, new_status = callback.data.split(":")
    order_id = int(order_id)
    order = await Order.get_or_none(id=order_id).prefetch_related("user")
    if not order:
        await callback.answer("Заказ не найден.", show_alert=True)
        return
    await order.update_from_dict({"status": new_status}).save()

    # Уведомляем клиента в Telegram
    status_label = dict(ORDER_STATUSES)[new_status]
    try:
        text = (
            "Сообщение для пользователя\n\n"
            f"Ваш заказ #{order.id} обновлён!\n\n"
            f"Текущий статус: <b>{status_label}</b>\n\n"
            f"Спасибо за покупку! Ожидайте дальнейших уведомлений."
        )
        await callback.bot.send_message(
            chat_id=order.user.id,
            text=text,
        )
    except Exception as e:
        # Логируем ошибку, если клиент заблокировал бота или ошибка отправки
        print(f"[OrderNotify] Не удалось отправить клиенту: {e}")

    # Возвращаем админа к деталям заказа
    await admin_show_order_summary(callback, state, order, order_id)
    await callback.answer("Статус заказа изменён, клиент уведомлён.")



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

@router.callback_query(F.data == 'admin_orders')
@admin_only
async def admin_orders_list(callback: CallbackQuery):
    """
    Displays the first page of the orders list.
	"""
    page = 1
    text = t('admin_orders.misc.b-spisok-zakazov-b-vyberi')
    await show_orders(callback, page, text)
    await callback.answer()

@router.callback_query(F.data.startswith('admin_orders_page:'))
@admin_only
async def admin_orders_page(callback: CallbackQuery):
    """
    Paginates through the orders list.
	"""
    page = int(callback.data.split(':')[1])
    text = f'📦 <b>Список заказов</b> (стр. {page}):'
    await show_orders(callback, page, text)
    await callback.answer()

@router.callback_query(F.data.startswith('admin_order_detail:'))
@admin_only
async def admin_order_detail(callback: CallbackQuery, t, state: FSMContext, **_):
    """
    Displays details of a single order.
	"""
    order_id = int(callback.data.split(':')[1])
    order = await get_order_by_id(order_id)
    if not order:
        await callback.answer(t('admin_orders.messages.zakaz-ne-najden'), show_alert=True)
        return
    await admin_show_order_summary(callback, state, order, order_id)
    await callback.answer()

@router.callback_query(F.data == 'change_status')
@admin_only
async def change_order_status_menu(callback: CallbackQuery, t, **_):
    """
    Displays a keyboard with order statuses.
    :param callback: Admin's CallbackQuery.
	"""
    message = callback.message
    order_id = int(message.text.split('#')[1].split()[0])
    order = await get_order_by_id(order_id)
    if not order:
        await callback.answer(t('admin_orders.messages.zakaz-ne-najden'), show_alert=True)
        return
    await message.edit_reply_markup(reply_markup=status_keyboard(order.id, order.status))
    await callback.answer()

@router.callback_query(F.data.startswith('admin_order_set_status:'))
@admin_only
async def set_order_status(callback: CallbackQuery, t, state: FSMContext, **_):
    """
    Saves the selected order status, notifies the customer, and returns to the order details.
	"""
    _, order_id, new_status = callback.data.split(':')
    order_id = int(order_id)
    order = await Order.get_or_none(id=order_id).prefetch_related('user')
    if not order:
        await callback.answer(t('admin_orders.messages.zakaz-ne-najden'), show_alert=True)
        return
    await order.update_from_dict({'status': new_status}).save()
    status_label = dict(ORDER_STATUSES)[new_status]
    try:
        text = f'Сообщение для пользователя\n\nВаш заказ #{order.id} обновлён!\n\nТекущий статус: <b>{status_label}</b>\n\nСпасибо за покупку! Ожидайте дальнейших уведомлений.'
        await callback.bot.send_message(chat_id=order.user.id, text=text)
    except Exception as e:
        print(f'[OrderNotify] Не удалось отправить клиенту: {e}')
    await admin_show_order_summary(callback, state, order, order_id)
    await callback.answer(t('admin_orders.messages.status-zakaza-izmenen-klient'))
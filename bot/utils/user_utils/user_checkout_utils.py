from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram import Bot
from bot.utils.common_utils import format_price
from config_data.env import ADMIN_IDS
from bot.keyboards.user.user_checkout_keyboards import payment_methods_keyboard
from bot.states.user_states.order_states import OrderStates
from bot.utils.user_utils.user_orders_utils import show_order_summary
from bot.utils.user_utils.validators import validate_name, format_name, validate_phone, validate_address
from bot.utils.user_utils.user_common_utils import validation_process_name, validation_process_address, validation_process_phone

async def editing_name(message: Message, state: FSMContext, t):
    """
    Handles entering a new full name in edit mode.
    Validates input and shows a summary.
    """
    name = message.text
    if not validate_name(name):
        await validation_process_name(message, state, t)
        return
    name = format_name(name)
    await state.update_data(name=name)
    await show_order_summary(message, state, t)

async def editing_phone(message: Message, state: FSMContext, t):
    """
    Handles entering a new phone number in edit mode.
    Validates input and shows a summary.
	"""
    phone = message.text
    if not validate_phone(phone):
        await validation_process_phone(message, state, t)
        return
    await state.update_data(phone=phone)
    await show_order_summary(message, state, t)

async def editing_address(message: Message, state: FSMContext, t):
    """
    Handles entering a new address in edit mode.
    Validates input and shows a summary.
	"""
    address = message.text
    if not validate_address(address):
        await validation_process_address(message, state, t)
        return
    await state.update_data(address=address)
    await show_order_summary(message, state, t)

async def editing_comment(message: Message, state: FSMContext, t):
    """
    Handles entering a new comment in edit mode.
    Validates input and shows a summary.
	"""
    comment = message.text
    await state.update_data(comment=comment)
    await show_order_summary(message, state, t)

async def editing_delivery(callback: CallbackQuery, t, state: FSMContext, **_):
    """
    Handles selecting a new delivery method in edit mode.
    Validates input and shows a summary.
	"""
    method = {'delivery_courier': 'Доставка курьером', 'delivery_pickup': t('user_checkout_keyboards.buttons.samovyvoz')}[callback.data]
    await state.update_data(delivery_method=method)
    if method == 'Доставка курьером':
        await callback.message.edit_text(t('user_checkout.messages.vvedite-adres-dostavki'))
        await state.set_state(OrderStates.editing_address)
        await callback.answer()
        return
    await callback.message.delete()
    await show_order_summary(callback, state, t)
    await callback.answer()

async def editing_payment(callback: CallbackQuery, t, state: FSMContext, **_):
    """
    Handles selecting a new payment method in edit mode.
    Validates input and shows a summary.
	"""
    method = {'pay_card': t('user_checkout_keyboards.buttons.kartoj-onlajn'), 'pay_cash': t('user_checkout_keyboards.buttons.nalichnye'), 'pay_yoomoney': t('user_checkout_keyboards.buttons.yumoney')}[callback.data]
    if method in (t('user_checkout_keyboards.buttons.kartoj-onlajn'), t('user_checkout_keyboards.buttons.yumoney')):
        try:
            await callback.message.edit_text(text=t('user_checkout.messages.etot-sposob-oplaty'), reply_markup=payment_methods_keyboard(t))
        except Exception as e:
            pass
        await callback.answer()
        return
    await state.update_data(payment_method=method)
    await callback.message.delete()
    await show_order_summary(callback, state, t)

async def notify_admin_about_new_order(bot: Bot, order, t):
    """
    Sends an admin notification about a new order.
	"""
    text = t('user_checkout_utils.misc.soobschenie-dlya-administratora').format(id=order.id, full_name=order.name, phone=order.phone, total=format_price(order.total_price), currency=t("currency"), order_status=order.status)
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(chat_id=int(admin_id), text=text)
        except Exception as e:
            print(f'Ошибка отправки уведомления админу: {e}')
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


async def editing_name(message: Message, state: FSMContext):
    """
    Обработка ввода нового ФИО в режиме редактирования.
    Проверяет валидность, показывает summary.
    """
    name = message.text
    if not validate_name(name):
        await validation_process_name(message, state)
        return
    name = format_name(name)
    await state.update_data(name=name)
    await show_order_summary(message, state)


async def editing_phone(message: Message, state: FSMContext):
    """
    Обработка ввода нового телефона в режиме редактирования.
    Проверяет валидность, показывает summary.
    """
    phone = message.text
    if not validate_phone(phone):
        await validation_process_phone(message, state)
        return
    await state.update_data(phone=phone)
    await show_order_summary(message, state)


async def editing_address(message: Message, state: FSMContext):
    """
    Обработка ввода нового адреса в режиме редактирования.
    Проверяет валидность, показывает summary.
    """
    address = message.text
    if not validate_address(address):
        await validation_process_address(message, state)
        return
    await state.update_data(address=address)
    await show_order_summary(message, state)


async def editing_comment(message: Message, state: FSMContext):
    """
    Обработка ввода нового комментария в режиме редактирования.
    Проверяет валидность, показывает summary.
    """
    comment = message.text
    await state.update_data(comment=comment)
    await show_order_summary(message, state)


async def editing_delivery(callback: CallbackQuery, state: FSMContext):
    """
    Обработка выбора нового метода доставки в режиме редактирования.
    Проверяет валидность, показывает summary.
    """
    method = {
        "delivery_courier": "Доставка курьером",
        "delivery_pickup": "Самовывоз"
    }[callback.data]

    await state.update_data(delivery_method=method)

    if method == "Доставка курьером":
        await callback.message.edit_text("Введите адрес доставки:")
        await state.set_state(OrderStates.editing_address)
        await callback.answer()
        return

    await callback.message.delete()
    await show_order_summary(callback, state)
    await callback.answer()


async def editing_payment(callback: CallbackQuery, state: FSMContext):
    """
    Обработка выбора нового метода оплаты в режиме редактирования.
    Проверяет валидность, показывает summary.
    """
    method = {
        "pay_card": "Картой онлайн",
        "pay_cash": "Наличные",
        "pay_yoomoney": "ЮMoney"
    }[callback.data]

    if method in ("Картой онлайн", "ЮMoney"):
        try:
            await callback.message.edit_text(
                text="❗️ Этот способ оплаты скоро появится. Пока выберите другой:",
                reply_markup=payment_methods_keyboard()
            )
        except Exception as e:
            pass
        await callback.answer()
        return
    await state.update_data(payment_method=method)
    await callback.message.delete()
    await show_order_summary(callback, state)


async def notify_admin_about_new_order(bot: Bot, order):
    """
    Отправляет админу уведомление о новом заказе.
    """
    text = (
        "Сообщение для администратора\n\n"
        f"🛒 <b>Новый заказ #{order.id}</b>\n"
        f"Имя: {order.name}\n"
        f"Телефон: {order.phone}\n"
        f"Сумма: {format_price(order.total_price)} ₽\n"
        f"Статус: {order.status}"
    )
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(chat_id=int(admin_id), text=text)
        except Exception as e:
            # Можно залогировать ошибку, если не критично
            print(f"Ошибка отправки уведомления админу: {e}")




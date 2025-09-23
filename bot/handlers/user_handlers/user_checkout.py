from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from database.crud import get_or_create_user_profile, get_cart, create_order, create_user_profile
from bot.states.user_states.order_states import OrderStates
from bot.keyboards.user.user_checkout_keyboards import checkout_edit_keyboard, payment_methods_keyboard, delivery_methods_keyboard, change_address_keyboard, profile_data_confirm_keyboard
from bot.keyboards.user.order_keyboards import order_details_keyboard
from bot.keyboards.user.user_common_keyboards import cart_back_menu
from bot.utils.user_utils.user_orders_utils import show_order_summary
from bot.utils.user_utils.universal_handlers import universal_address_handler, universal_phone_handler, universal_name_handler, universal_exit
from bot.utils.user_utils.user_common_utils import send_step_and_cleanup, start_manual_checkout
from bot.utils.common_utils import delete_request_and_user_message
from bot.utils.user_utils.user_checkout_utils import editing_name, editing_phone, editing_address, editing_delivery, editing_payment, editing_comment, notify_admin_about_new_order
router = Router()

@router.callback_query(lambda c: c.data in ['menu_catalog', 'menu_main'])
async def checkout_exit_handler(callback: CallbackQuery, state: FSMContext):
    """
    Handler for exiting the checkout process via the “Catalog” or “Main Menu” buttons.
    Calls the universal exit function.
	"""
    await universal_exit(callback, state)

@router.callback_query(F.data == 'place_an_order')
async def place_an_order_handler(callback: CallbackQuery, t, state: FSMContext, **_):
    """
    Starts the checkout process. Checks the cart.
    If a profile exists — suggests using it. Otherwise, enns a step-by-step input flow.
	"""
    await delete_request_and_user_message(callback.message, state)
    user_id = callback.from_user.id
    user_profile = await get_or_create_user_profile(user_id)
    cart_items = await get_cart(user_id)
    if not cart_items:
        await callback.message.answer(t('user_checkout.messages.vasha-korzina-pusta'), reply_markup=cart_back_menu())
        return
    await state.update_data(cart=[{'product_id': item.product_id, 'qty': item.quantity} for item in cart_items])
    fields_to_check = ['full_name', 'phone', 'address']
    if user_profile and all((getattr(user_profile, field) not in ('', None, '-') for field in fields_to_check)):
        text = f'В вашем профиле:\n\nФИО: {user_profile.full_name}\nТелефон: {user_profile.phone}\nАдрес: {user_profile.address}\n\nИспользовать эти данные для оформления заказа?'
        await callback.message.answer(text, reply_markup=profile_data_confirm_keyboard())
        await state.set_state(OrderStates.use_profile_choice)
    else:
        await start_manual_checkout(callback, state)
        await state.set_state(OrderStates.waiting_for_name)
    await callback.answer()

@router.callback_query(OrderStates.use_profile_choice)
async def use_profile_choice_handler(callback: CallbackQuery, t, state: FSMContext, **_):
    """
    Handles the user's choice: use profile data or fill in again.
	"""
    await delete_request_and_user_message(callback.message, state)
    user_id = callback.from_user.id
    user_profile = await get_or_create_user_profile(user_id)
    if callback.data == 'use_profile':
        await state.update_data(name=user_profile.full_name, phone=user_profile.phone, address=user_profile.address)
        comment = await callback.message.answer(t('user_checkout.messages.vvedite-kommentarij-k-zakazu'), reply_markup=cart_back_menu())
        await state.update_data(main_message_id=comment.message_id)
        await state.set_state(OrderStates.waiting_for_comment)
    elif callback.data == 'fill_manually':
        await start_manual_checkout(callback, state)
        await state.set_state(OrderStates.waiting_for_name)
    elif callback.data == 'cancel_order':
        await callback.message.answer(t('user_checkout.messages.oformlenie-zakaza-otmeneno'), reply_markup=cart_back_menu())
        await state.clear()
    await callback.answer()

@router.message(OrderStates.waiting_for_name)
async def name_handler_order(message: Message, state: FSMContext):
    """
    Handler for entering the name during checkout.
    Calls the generic name handler.
	"""
    await universal_name_handler(message, state)

@router.message(OrderStates.editing_name)
async def edit_name_handler_order(message: Message, state: FSMContext):
    """
    Handler for editing the name during checkout.
	"""
    await editing_name(message, state)

@router.message(OrderStates.waiting_for_phone)
async def phone_handler_order(message: Message, state: FSMContext):
    """
    Handler for entering the phone number during checkout.
    Calls the generic phone handler.
	"""
    await universal_phone_handler(message, state)

@router.message(OrderStates.editing_phone)
async def edit_phone_handler_order(message: Message, state: FSMContext):
    """
    Handler for editing the phone number during checkout.
	"""
    await editing_phone(message, state)

@router.message(OrderStates.waiting_for_comment)
async def order_comment_handler(message: Message, state: FSMContext):
    """
    Saves the user's comment and proceeds to payment method selection.
	"""
    await delete_request_and_user_message(message, state)
    await state.update_data(comment=message.text if message.text != '-' else 'Без комментария')
    data = await state.get_data()
    text = f"Пожалуйста, заполните данные для заказа.\n\n✅ Фамилия и имя: {data.get('name')}\n✅ Телефон: {data.get('phone')}\n✅ Комментарий: {data.get('comment')}\n4️⃣ Выберите способ оплаты:"
    await send_step_and_cleanup(message=message, text=text, state=state, reply_markup=payment_methods_keyboard())
    await state.set_state(OrderStates.choosing_payment)

@router.message(OrderStates.editing_comment)
async def edit_comment_handler_order(message: Message, state: FSMContext):
    """
    Handler for editing the order comment.
	"""
    await editing_comment(message, state)

@router.callback_query(OrderStates.choosing_payment)
async def choose_payment_method(callback: CallbackQuery, t, state: FSMContext, **_):
    """
    Handles the user's selection of payment method.
	"""
    await delete_request_and_user_message(callback.message, state)
    method = {'pay_card': t('user_checkout_keyboards.buttons.kartoj-onlajn'), 'pay_cash': t('user_checkout_keyboards.buttons.nalichnye'), 'pay_yoomoney': t('user_checkout_keyboards.buttons.yumoney')}[callback.data]
    if not method:
        await callback.answer(t('user_checkout.messages.neizvestnyj-sposob-oplaty'), show_alert=True)
        return
    if method in (t('user_checkout_keyboards.buttons.kartoj-onlajn'), t('user_checkout_keyboards.buttons.yumoney')):
        try:
            await callback.message.answer(text=t('user_checkout.messages.etot-sposob-oplaty'), reply_markup=payment_methods_keyboard())
        except Exception as e:
            pass
        await callback.answer()
        return
    await state.update_data(payment_method=method)
    data = await state.get_data()
    text = f"Пожалуйста, заполните данные для заказа.\n\n✅ Фамилия и имя: {data.get('name')}\n✅ Телефон: {data.get('phone')}\n✅ Комментарий: {data.get('comment')}\n✅ Способ оплаты: {data.get('payment_method')}\n5️⃣ Выберите способ доставки:"
    await send_step_and_cleanup(message=callback.message, text=text, state=state, reply_markup=delivery_methods_keyboard())
    await state.set_state(OrderStates.choosing_delivery)
    await callback.answer()

@router.callback_query(OrderStates.editing_payment)
async def edit_payment_handler_order(callback: CallbackQuery, state: FSMContext):
    """
    Handler for editing the payment method of the order.
	"""
    await editing_payment(callback, state)

@router.callback_query(OrderStates.choosing_delivery)
async def choose_delivery_method(callback: CallbackQuery, t, state: FSMContext, **_):
    """
    Handles the user's selection of delivery method.
	"""
    method = {'delivery_courier': 'Доставка курьером', 'delivery_pickup': t('user_checkout_keyboards.buttons.samovyvoz')}[callback.data]
    await state.update_data(delivery_method=method)
    if method == 'Доставка курьером':
        await delete_request_and_user_message(callback.message, state)
        user_profile = await get_or_create_user_profile(callback.from_user.id)
        if user_profile.address not in ('', '-', None):
            msg = await callback.message.answer(f"Текущий адрес из профиля:\n{(user_profile.address if user_profile and hasattr(user_profile, 'address') else 'Нет адреса')}\n\nХотите использовать этот адрес для доставки или ввести новый?", reply_markup=change_address_keyboard())
            await state.update_data(main_message_id=msg.message_id)
            await state.set_state(OrderStates.choose_address_option)
        else:
            msg = await callback.message.answer(t('user_checkout.messages.vvedite-adres-dostavki'), reply_markup=cart_back_menu())
            await state.update_data(main_message_id=msg.message_id)
            await state.set_state(OrderStates.waiting_for_address)
    else:
        await delete_request_and_user_message(callback.message, state)
        await state.update_data(address='Не требуется')
        await show_order_summary(callback, state)
    await callback.answer()

@router.callback_query(OrderStates.editing_delivery)
async def edit_delivery_handler_order(callback: CallbackQuery, state: FSMContext):
    """
    Handler for editing the delivery method of the order.
	"""
    await editing_delivery(callback, state)

@router.callback_query(OrderStates.choose_address_option)
async def choose_address_option_handler(callback: CallbackQuery, t, state: FSMContext, **_):
    """
    Handles address selection: use from profile or enter a new one.
	"""
    await delete_request_and_user_message(callback.message, state)
    user_id = callback.from_user.id
    user_profile = await get_or_create_user_profile(user_id)
    if callback.data == 'use_profile_address':
        address = user_profile.address or 'Не указан'
        await state.update_data(address=address)
        await show_order_summary(callback, state)
    elif callback.data == 'enter_new_address':
        msg = await callback.message.answer(t('user_checkout.messages.vvedite-adres-dostavki'), reply_markup=cart_back_menu())
        await state.update_data(address=msg.text)
        await state.update_data(main_message_id=msg.message_id)
        await state.set_state(OrderStates.waiting_for_address)
    await callback.answer()

@router.message(OrderStates.waiting_for_address)
async def address_handler_order(message: Message, state: FSMContext):
    """
    Handles address input during checkout (asynchronous, with validation).
	"""
    await universal_address_handler(message, state)

@router.message(OrderStates.editing_address)
async def edit_address_handler_order(message: Message, state: FSMContext):
    """
    Handler for editing the delivery address of the order.
	"""
    await editing_address(message, state)

@router.callback_query(OrderStates.confirm, F.data == 'edit_data')
async def edit_data_handler(callback: CallbackQuery, t, state: FSMContext, **_):
    """
    Switches the user into order data editing mode.
    Displays a keyboard to choose which field to edit.
	"""
    await delete_request_and_user_message(callback.message, state)
    edit_msg = await callback.message.answer(t('user_checkout.messages.chto-vy-hotite-izmenit'), reply_markup=checkout_edit_keyboard())
    await state.update_data(main_message_id=edit_msg.message_id)
    await callback.answer()

@router.callback_query(OrderStates.confirm, F.data == 'edit_name')
async def edit_name_callback(callback: CallbackQuery, t, state: FSMContext, **_):
    """
    Start editing the full name.
	"""
    await delete_request_and_user_message(callback.message, state)
    msg = await callback.message.answer(t('user_checkout.messages.vvedite-novye-fio'), reply_markup=cart_back_menu())
    await state.update_data(main_message_id=msg.message_id)
    await state.set_state(OrderStates.editing_name)
    await callback.answer()

@router.callback_query(OrderStates.confirm, F.data == 'edit_phone')
async def edit_phone_callback(callback: CallbackQuery, t, state: FSMContext, **_):
    """
    Start editing the phone number.
	"""
    await delete_request_and_user_message(callback.message, state)
    msg = await callback.message.answer(t('user_checkout.messages.vvedite-novyj-telefon'), reply_markup=cart_back_menu())
    await state.update_data(main_message_id=msg.message_id)
    await state.set_state(OrderStates.editing_phone)
    await callback.answer()

@router.callback_query(OrderStates.confirm, F.data == 'edit_address')
async def edit_address_callback(callback: CallbackQuery, t, state: FSMContext, **_):
    """
    Start editing the address.
	"""
    await delete_request_and_user_message(callback.message, state)
    msg = await callback.message.answer(t('user_checkout.messages.vvedite-novyj-adres'), reply_markup=cart_back_menu())
    await state.update_data(main_message_id=msg.message_id)
    await state.set_state(OrderStates.editing_address)
    await callback.answer()

@router.callback_query(OrderStates.confirm, F.data == 'edit_comment')
async def edit_comment_callback(callback: CallbackQuery, t, state: FSMContext, **_):
    """
    Start editing the comment.
	"""
    await delete_request_and_user_message(callback.message, state)
    msg = await callback.message.answer(t('user_checkout.messages.vvedite-novyj-kommentarij-ili'), reply_markup=cart_back_menu())
    await state.update_data(main_message_id=msg.message_id)
    await state.set_state(OrderStates.editing_comment)
    await callback.answer()

@router.callback_query(OrderStates.confirm, F.data == 'edit_payment')
async def edit_payment_callback(callback: CallbackQuery, t, state: FSMContext, **_):
    """
    Start editing the payment method.
	"""
    await delete_request_and_user_message(callback.message, state)
    msg = await callback.message.answer(t('user_checkout.messages.vyberite-sposob-oplaty'), reply_markup=payment_methods_keyboard())
    await state.update_data(main_message_id=msg.message_id)
    await state.set_state(OrderStates.editing_payment)
    await callback.answer()

@router.callback_query(OrderStates.confirm, F.data == 'edit_delivery')
async def edit_delivery_callback(callback: CallbackQuery, t, state: FSMContext, **_):
    """
    Start editing the delivery method.
	"""
    await delete_request_and_user_message(callback.message, state)
    msg = await callback.message.answer(t('user_checkout.messages.vyberite-sposob-dostavki'), reply_markup=delivery_methods_keyboard())
    await state.update_data(main_message_id=msg.message_id)
    await state.set_state(OrderStates.editing_delivery)
    await callback.answer()

@router.callback_query(OrderStates.confirm, F.data == 'back_to_confirm')
async def back_to_summary_callback(callback: CallbackQuery, state: FSMContext):
    """
    Return to the order summary.
	"""
    await delete_request_and_user_message(callback.message, state)
    await show_order_summary(callback, state)
    await callback.answer()

@router.callback_query(OrderStates.confirm, F.data == 'confirm_order')
async def order_confirm_handler(callback: CallbackQuery, t, state: FSMContext, **_):
    """
    Confirms checkout, adds the order to the database, clears the cart, and notifies the user.
	"""
    await delete_request_and_user_message(callback.message, state)
    user_id = callback.from_user.id
    data = await state.get_data()
    bot = callback.bot
    order = await create_order(user_id=user_id, name=data.get('name'), phone=data.get('phone'), payment_method=data.get('payment_method'), delivery_method=data.get('delivery_method'), address=data.get('address'), comment=data.get('comment'))
    await notify_admin_about_new_order(bot, order)
    await create_user_profile(user_id=user_id, name=data.get('name'), phone=data.get('phone'), address=data.get('address'))
    if not order:
        await callback.message.answer(t('user_checkout.messages.korzina-pusta'), reply_markup=cart_back_menu())
        await state.clear()
        await callback.answer()
        return
    await callback.message.answer(t('user_checkout.messages.spasibo-vash-zakaz-oformlen'), reply_markup=order_details_keyboard())
    await state.clear()
    await callback.answer()

@router.callback_query(F.data == 'cancel_order')
async def cancel_order(callback: CallbackQuery, t, state: FSMContext, **_):
    """
    Handles order cancellation.
    Clears the FSM state and notifies the user.
	"""
    await callback.message.edit_text(t('user_checkout.messages.oformlenie-zakaza-otmeneno'), reply_markup=cart_back_menu())
    await state.clear()
    await callback.answer()
from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.handlers.user_handlers.user_catalog import show_categories
from bot.keyboards.user.user_main_menu import main_menu
from bot.states.user_states.order_states import OrderStates
from bot.states.user_states.profile_states import ProfileStates
from bot.keyboards.user.user_common_keyboards import cart_back_menu
from bot.utils.user_utils.user_orders_utils import show_order_summary
from bot.utils.user_utils.user_profile_utils import show_profile_summary
from bot.utils.user_utils.validators import validate_name, format_name, validate_phone, validate_address
from bot.utils.user_utils.user_common_utils import send_step_and_cleanup, validation_process_name, validation_process_phone, validation_process_address
from bot.utils.common_utils import delete_request_and_user_message
from database.crud import create_user_profile
router = Router()

async def universal_name_handler(message: Message, state: FSMContext, t) -> None:
    """
    Full name handler for checkout and profile. After successful input, immediately shows the phone step.
    Messages are always cleared.
	"""
    await delete_request_and_user_message(message, state)
    name = message.text
    if not validate_name(name):
        await validation_process_name(message, state, t)
        return
    name = format_name(name)
    await state.update_data(name=name)
    state_name = await state.get_state()
    text = t('universal_handlers.misc.zapolnite-dannye-fio').format(name=name)
    await send_step_and_cleanup(message, text, state, reply_markup=cart_back_menu(t))
    if state_name == OrderStates.waiting_for_name.state:
        await state.set_state(OrderStates.waiting_for_phone)
    elif state_name == ProfileStates.waiting_for_name.state:
        await state.set_state(ProfileStates.waiting_for_phone)

async def universal_phone_handler(message: Message, state: FSMContext, t) -> None:
    """
    Phone number handler for checkout and profile. After successful input, shows the next step: comment (checkout) or address (profile).
    Messages are always cleared.
	"""
    await delete_request_and_user_message(message, state)
    phone = message.text
    if not validate_phone(phone):
        await validation_process_phone(message, state, t)
        return
    await state.update_data(phone=phone)
    data = await state.get_data()
    name = data.get('name', '-')
    state_name = await state.get_state()
    if state_name == OrderStates.waiting_for_phone.state:
        text = t('universal_handlers.misc.zapolnite-dannye-fio.2').format(name=name, phone=phone)
        await send_step_and_cleanup(message, text, state, reply_markup=cart_back_menu(t))
        await state.set_state(OrderStates.waiting_for_comment)
    elif state_name == ProfileStates.waiting_for_phone.state:
        text = t('universal_handlers.misc.zapolnite-dannye-profilya').format(name=name, phone=phone)
        await send_step_and_cleanup(message, text, state, reply_markup=cart_back_menu(t))
        await state.set_state(ProfileStates.waiting_for_address)

async def universal_address_handler(message: Message, state: FSMContext, t) -> None:
    """
    Address handler for the profile. After successful input, shows the summary and editing keyboard.
    Messages are always cleared.
	"""
    await delete_request_and_user_message(message, state)
    address = message.text
    if not validate_address(address):
        await validation_process_address(message, state, t)
        return
    await state.update_data(address=address)
    data = await state.get_data()
    state_name = await state.get_state()
    if state_name == OrderStates.waiting_for_address.state:
        await show_order_summary(message, state, t)
    elif state_name == ProfileStates.waiting_for_address.state:
        user_id = message.from_user.id
        await create_user_profile(user_id=user_id, name=data.get('name', ''), phone=data.get('phone', ''), address=address)
        await show_profile_summary(message, state, user_id, t)

async def universal_exit(callback: CallbackQuery, t, state: FSMContext, **_):
    """
    Universal function to exit the current scenario (checkout, etc.).
    Clears previous messages and resets the FSM state.
    
    :param callback: User's CallbackQuery object.
    :param state: FSM context.
	"""
    await delete_request_and_user_message(callback.message, state)
    if callback.data == 'menu_catalog':
        await show_categories(callback, t)
    elif callback.data == 'menu_main':
        await callback.message.answer(t('universal_handlers.messages.vy-vernulis-v-glavnoe'), reply_markup=main_menu(t))
    await state.clear()
    await callback.answer()
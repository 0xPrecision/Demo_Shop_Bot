from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.keyboards.user.user_profile_keyboards import profile_confirm_or_edit_keyboard
from bot.states.user_states.profile_states import ProfileStates
from bot.utils.common_utils import delete_request_and_user_message
from bot.utils.user_utils.user_common_utils import (
    validation_process_address,
    validation_process_name,
    validation_process_phone,
)
from bot.utils.user_utils.validators import (
    format_name,
    validate_address,
    validate_name,
    validate_phone,
)
from database.crud import get_or_create_user_profile


async def show_profile_summary(
    message: Message, state: FSMContext, user_id: int, t
) -> None:
    """
    Displays the user's profile with a short summary and confirmation/edit keyboard.

    After displaying the profile, automatically sets FSM to ProfileStates.confirm
    to handle further actions (e.g., editing data).

    :param message: aiogram.types Message object where the profile is shown.
    :param state: User's FSMContext (aiogram), used for storing/fetching data and changing state.
    :param user_id: int. User's ID.
    :return: None.
    """
    await delete_request_and_user_message(message, state)
    user_profile = await get_or_create_user_profile(user_id)
    data = await state.get_data()
    name = data.get("name") or user_profile.full_name or "-"
    phone = data.get("phone") or user_profile.phone or "-"
    address = data.get("address") or user_profile.address or "-"
    text = t("user_profile_utils.misc.b-vash-profil-b-b-fio-b").format(
        name=name, phone=phone, address=address
    )
    await message.answer(text, reply_markup=profile_confirm_or_edit_keyboard(t))
    await state.set_state(ProfileStates.confirm)


async def editing_name(message: Message, state: FSMContext, t):
    """
    Handles entering a new full name in edit mode.
    Validates input, updates the profile, and shows a summary.
    """
    user_id = message.from_user.id
    name = message.text
    if not validate_name(name):
        await validation_process_name(message, state, t)
        return
    name = format_name(name)
    await state.update_data(name=name)
    await show_profile_summary(message, state, user_id, t)


async def editing_phone(message: Message, state: FSMContext, t):
    """
    Handles entering a new phone number in edit mode.
    Validates input, updates the profile, and shows a summary.
    """
    user_id = message.from_user.id
    phone = message.text
    if not validate_phone(phone):
        await validation_process_phone(message, state, t)
        return
    await state.update_data(phone=phone)
    await show_profile_summary(message, state, user_id, t)


async def editing_address(message: Message, state: FSMContext, t):
    """
    Handles entering a new address in edit mode.
    Validates input, updates the profile, and shows a summary.
    """
    user_id = message.from_user.id
    address = message.text
    if not validate_address(address):
        await validation_process_address(message, state, t)
        return
    await state.update_data(address=address)
    await show_profile_summary(message, state, user_id, t)

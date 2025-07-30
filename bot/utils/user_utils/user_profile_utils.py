from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.keyboards.user.user_profile_keyboards import profile_confirm_or_edit_keyboard
from bot.states.user_states.profile_states import ProfileStates
from bot.utils.user_utils.user_common_utils import validation_process_name, validation_process_address, validation_process_phone
from bot.utils.common_utils import delete_request_and_user_message
from bot.utils.user_utils.validators import validate_name, format_name, validate_phone, validate_address
from database.crud import get_or_create_user_profile

async def show_profile_summary(message: Message, state: FSMContext, user_id: int) -> None:
    """
    Показывает пользователю его профиль с краткой сводкой и клавиатурой подтверждения/редактирования.

    После отображения профиля автоматически переводит FSM в состояние ProfileStates.confirm,
    чтобы обрабатывать дальнейшие действия (например, изменение данных).

    :param message: Объект aiogram.types Message, куда выводится профиль.
    :param state: FSMContext пользователя (aiogram), используется для хранения и получения данных, а также смены состояния.
    :param user_id: int. User ID пользователя
    :return: None
    """
    await delete_request_and_user_message(message, state)
    user_profile = await get_or_create_user_profile(user_id)
    data = await state.get_data()
    name = data.get("name") or user_profile.full_name or "-"
    phone = data.get("phone") or user_profile.phone or "-"
    address = data.get("address") or user_profile.address or "-"

    sep = "-" * 24
    text = (f"👤 <b>Ваш профиль</b>\n"
            f"{sep}\n\n"
            f"<b>ФИО:</b> {name}\n"
            f"<b>Телефон:</b> {phone}\n"
            f"<b>Адрес:</b> {address}\n\n"
            f"{sep}\n"
            f"❓ <i>Данные корректны?</i>")

    await message.answer(text, reply_markup=profile_confirm_or_edit_keyboard())
    await state.set_state(ProfileStates.confirm)


async def editing_name(message: Message, state: FSMContext):
    """
    Обработка ввода нового ФИО в режиме редактирования.
    Проверяет валидность, обновляет профиль, показывает summary.
    """
    user_id = message.from_user.id
    name = message.text
    if not validate_name(name):
        await validation_process_name(message, state)
        return
    name = format_name(name)
    await state.update_data(name=name)
    await show_profile_summary(message, state, user_id)


async def editing_phone(message: Message, state: FSMContext):
    """
    Обработка ввода нового телефона в режиме редактирования.
    Проверяет валидность, обновляет профиль, показывает summary.
    """
    user_id = message.from_user.id
    phone = message.text
    if not validate_phone(phone):
        await validation_process_phone(message, state)
        return
    await state.update_data(phone=phone)
    await show_profile_summary(message, state, user_id)


async def editing_address(message: Message, state: FSMContext):
    """
    Обработка ввода нового адреса в режиме редактирования.
    Проверяет валидность, обновляет профиль, показывает summary.
    """
    user_id = message.from_user.id
    address = message.text
    if not validate_address(address):
        await validation_process_address(message, state)
        return
    await state.update_data(address=address)
    await show_profile_summary(message, state, user_id)
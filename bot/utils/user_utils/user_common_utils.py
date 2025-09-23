from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.keyboards.user.user_common_keyboards import cart_back_menu


async def delete_user_message_safe(message: Message) -> None:
    """
    Safely deletes the user's message.
	"""
    try:
        await message.delete()
    except Exception:
        pass


async def start_manual_checkout(message_or_callback, state: FSMContext):
    """
    Full name handler for checkout and profile, supports edit mode.
    After successful input, immediately shows the phone step (if not edit).
    Messages are always cleared.
	"""
    if hasattr(message_or_callback, "message"):
        # Это CallbackQuery
        target_message = message_or_callback.message
    else:
        # Это Message
        target_message = message_or_callback

    main_msg = await target_message.answer(
        "Пожалуйста, заполните данные.\n\n"
        "1️⃣ ФИО:",
        reply_markup=cart_back_menu()
    )
    await state.update_data(main_message_id=main_msg.message_id)


async def validation_process_name(message: Message, state: FSMContext):
    """
    Shows a warning about an invalid full name.
    :param message: User message.
    :param state: FSMContext for storing main_message_id.
	"""
    warn = await message.answer(
        "Пожалуйста, введите корректное имя (только буквы, минимум 2 символа).",
        reply_markup=cart_back_menu()
    )
    await state.update_data(main_message_id=warn.message_id)

async def validation_process_phone(message: Message, state: FSMContext):
    """
    Shows a warning about an invalid phone number.
    :param message: User message.
    :param state: FSMContext for storing main_message_id.
	"""
    warn = await message.answer(
        "Пожалуйста, введите корректный телефон (только цифры).",
        reply_markup=cart_back_menu()
    )
    await state.update_data(main_message_id=warn.message_id)

async def validation_process_address(message: Message, state: FSMContext):
    """
    Shows a warning about an invalid address.
    :param message: User message.
    :param state: FSMContext for storing main_message_id.
	"""
    warn = await message.answer(
        "Пожалуйста, введите корректный адрес (пример: г. Москва, ул. Ленина, д. 15):",
        reply_markup=cart_back_menu()
    )
    await state.update_data(main_message_id=warn.message_id)


async def send_step_and_cleanup(
    message: Message,
    text: str,
    state: FSMContext,
    reply_markup=None,
    main_message_id_key: str = "main_message_id"
) -> None:
    """
    Universal step sender: sends a message, deletes the old one, and saves main_message_id.
    
    :param message: User message.
    :param text: Text to send.
    :param state: FSMContext.
    :param reply_markup: Keyboard (default None).
    :param main_message_id_key: Key for storing the id (default main_message_id).
	"""
    msg = await message.answer(text, reply_markup=reply_markup)
    await delete_user_message_safe(message)
    await state.update_data(**{main_message_id_key: msg.message_id})






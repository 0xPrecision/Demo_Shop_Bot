from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.keyboards.user.user_common_keyboards import cart_back_menu


async def delete_user_message_safe(message: Message) -> None:
    """
    Безопасно удаляет сообщение пользователя.
    """
    try:
        await message.delete()
    except Exception:
        pass


async def start_manual_checkout(message_or_callback, state: FSMContext):
    """
    Обработчик ФИО для чекаута и профиля, поддерживает edit mode.
    После успешного ввода сразу показывает шаг с телефоном (если не edit).
    Сообщения всегда очищаются.
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
    Показывает предупреждение о некорректном ФИО.
    :param message: Сообщение пользователя.
    :param state: FSMContext для сохранения main_message_id.
    """
    warn = await message.answer(
        "Пожалуйста, введите корректное имя (только буквы, минимум 2 символа).",
        reply_markup=cart_back_menu()
    )
    await state.update_data(main_message_id=warn.message_id)

async def validation_process_phone(message: Message, state: FSMContext):
    """
    Показывает предупреждение о некорректном номере телефона.
    :param message: Сообщение пользователя.
    :param state: FSMContext для сохранения main_message_id.
    """
    warn = await message.answer(
        "Пожалуйста, введите корректный телефон (только цифры).",
        reply_markup=cart_back_menu()
    )
    await state.update_data(main_message_id=warn.message_id)

async def validation_process_address(message: Message, state: FSMContext):
    """
    Показывает предупреждение о некорректном адресе.
    :param message: Сообщение пользователя.
    :param state: FSMContext для сохранения main_message_id.
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
    Универсальная отправка шага: отправляет сообщение, удаляет старое, сохраняет main_message_id.

    :param message: Сообщение пользователя.
    :param text: Текст для отправки.
    :param state: FSMContext.
    :param reply_markup: Клавиатура (по умолчанию None).
    :param main_message_id_key: Ключ для хранения id (по умолчанию main_message_id).
    """
    msg = await message.answer(text, reply_markup=reply_markup)
    await delete_user_message_safe(message)
    await state.update_data(**{main_message_id_key: msg.message_id})






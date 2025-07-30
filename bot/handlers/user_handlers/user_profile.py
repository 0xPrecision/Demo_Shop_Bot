from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from bot.utils.user_utils.user_profile_utils import show_profile_summary, editing_name, editing_phone, editing_address
from bot.utils.user_utils.universal_handlers import universal_phone_handler, universal_name_handler, universal_address_handler
from bot.utils.user_utils.user_common_utils import start_manual_checkout
from bot.utils.common_utils import delete_request_and_user_message
from bot.utils.user_utils.validators import is_profile_complete
from bot.keyboards.user.user_profile_keyboards import edit_profile_keyboard, profile_menu_keyboard, profile_orders_keyboard, create_profile
from bot.keyboards.user.user_common_keyboards import cart_back_menu
from bot.states.user_states.profile_states import ProfileStates

from database.crud import get_or_create_user_profile, update_user_profile

router = Router()


@router.callback_query(F.data == "menu_profile")
async def show_profile_menu(callback: CallbackQuery, state: FSMContext):
    """
    Показывает главное меню профиля.
    """
    await state.clear()
    await delete_request_and_user_message(callback.message, state)
    text = (f"<b>    👤 Вы в меню пользователя</b>\n"
            f"{"-" * 36}\n\n"
            f"Выберите, что хотите посмотреть:")

    await callback.message.answer(text, reply_markup=profile_menu_keyboard())
    await callback.answer()


@router.callback_query(F.data == "my_orders")
async def show_profile_orders_menu(callback: CallbackQuery, state: FSMContext):
    """
    Показывает меню заказов пользователя.
    """
    await delete_request_and_user_message(callback.message, state)
    await callback.message.answer('Я хочу посмотреть:',
                                     reply_markup=profile_orders_keyboard())
    await callback.answer()


@router.callback_query(F.data == "my_data")
async def show_profile_data(callback: CallbackQuery, state: FSMContext):
    """
    Проверяет наличие и полноту профиля. Показывает данные или предлагает создать профиль.
    """
    user_id = callback.from_user.id
    user_profile = await get_or_create_user_profile(user_id)
    if user_profile and is_profile_complete(user_profile):
        await show_profile_summary(callback.message, state, user_id)
    else:
        await callback.message.edit_text('Ваш профиль отсутствует, хотите создать его сейчас?',
                                         reply_markup=create_profile())
        await state.set_state(ProfileStates.create_profile)

    await callback.answer()


@router.callback_query(ProfileStates.create_profile, F.data == "create_profile")
async def profile_create_start(callback: CallbackQuery, state: FSMContext):
    """
    Старт создания профиля пользователя.
    """
    await start_manual_checkout(callback, state)
    await state.set_state(ProfileStates.waiting_for_name)
    await callback.answer()


@router.message(ProfileStates.waiting_for_name)
async def profile_name_handler(message: Message, state: FSMContext):
    """
    Обработка ввода ФИО при создании профиля.
    """
    await universal_name_handler(message, state)


@router.message(ProfileStates.editing_name)
async def edit_profile_name_handler(message: Message, state: FSMContext):
    """
    Обработка ввода ФИО в режиме редактирования профиля.
    """
    await delete_request_and_user_message(message, state)
    await editing_name(message, state)


@router.message(ProfileStates.waiting_for_phone)
async def profile_phone_handler(message: Message, state: FSMContext):
    """
    Обработка ввода телефона при создании профиля.
    """
    await universal_phone_handler(message, state)


@router.message(ProfileStates.editing_phone)
async def edit_profile_phone_handler(message: Message, state: FSMContext):
    """
    Обработка ввода телефона в режиме редактирования профиля.
    """
    await delete_request_and_user_message(message, state)
    await editing_phone(message, state)


@router.message(ProfileStates.waiting_for_address)
async def profile_address_handler(message: Message, state: FSMContext):
    """
    Обработка ввода адреса при создании профиля.
    """
    await universal_address_handler(message, state)


@router.message(ProfileStates.editing_address)
async def edit_profile_address_handler(message: Message, state: FSMContext):
    """
    Обработка ввода адреса в режиме редактирования профиля.
    """
    await delete_request_and_user_message(message, state)
    await editing_address(message, state)



@router.callback_query(F.data == "confirm_profile")
async def confirm_profile(callback: CallbackQuery, state: FSMContext):
    """
    Подтверждение создания профиля.
    """
    user_id = callback.from_user.id
    await delete_request_and_user_message(callback.message, state)
    cur_state = await state.get_state()
    data = await state.get_data()
    if cur_state == ProfileStates.create_profile:
        await callback.message.answer('Ваш профиль успешно создан ✅',
                                      reply_markup=cart_back_menu())

    elif cur_state == ProfileStates.confirm:
        await update_user_profile(user_id,
                                  name=data.get("name"),
                                  phone=data.get("phone"),
                                  address=data.get("address"))

        await callback.message.answer('Ваш профиль успешно обновлён ✅',
                                      reply_markup=cart_back_menu())
        await state.clear()
    await callback.answer()


@router.callback_query(ProfileStates.confirm, F.data == "edit_profile")
async def edit_data_handler(callback: CallbackQuery, state: FSMContext):
    """
    Переводит пользователя в режим редактирования данных.
    Показывает клавиатуру с выбором поля для редактирования.
    """
    await delete_request_and_user_message(callback.message, state)
    edit_msg = await callback.message.answer("Что вы хотите изменить?",
                                                reply_markup=edit_profile_keyboard())
    await state.update_data(main_message_id=edit_msg.message_id)
    await callback.answer()


@router.callback_query(ProfileStates.confirm, F.data == "edit_profile_name")
async def edit_profile_name_callback(callback: CallbackQuery, state: FSMContext):
    """
    Начало редактирования ФИО.
    """
    await delete_request_and_user_message(callback.message, state)
    msg = await callback.message.answer("Введите новые ФИО:", reply_markup=cart_back_menu())
    await state.update_data(main_message_id=msg.message_id)
    await state.set_state(ProfileStates.editing_name)
    await callback.answer()


@router.callback_query(ProfileStates.confirm, F.data == "edit_profile_phone")
async def edit_profile_phone_callback(callback: CallbackQuery, state: FSMContext):
    """
    Начало редактирования телефона.
    """
    await delete_request_and_user_message(callback.message, state)
    msg = await callback.message.answer("Введите новый телефон:", reply_markup=cart_back_menu())
    await state.update_data(main_message_id=msg.message_id)
    await state.set_state(ProfileStates.editing_phone)
    await callback.answer()


@router.callback_query(ProfileStates.confirm, F.data == "edit_profile_address")
async def edit_profile_address_callback(callback: CallbackQuery, state: FSMContext):
    """
    Начало редактирования адреса.
    """
    await delete_request_and_user_message(callback.message, state)
    msg = await callback.message.answer("Введите новый адрес:", reply_markup=cart_back_menu())
    await state.update_data(main_message_id=msg.message_id)
    await state.set_state(ProfileStates.editing_address)
    await callback.answer()


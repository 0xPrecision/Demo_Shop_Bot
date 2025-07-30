from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.handlers.admin_handlers.add_product import add_product_category
from bot.handlers.admin_handlers.admin_access import admin_only
from bot.keyboards.admin.catalog_keyboards import back_menu
from bot.states.admin_states.category_states import CategoryStates
from bot.utils.common_utils import delete_request_and_user_message
from database.crud import create_category

router = Router()


@router.callback_query(F.data == "admin_add_category")
@admin_only
async def start_add_category(callback: CallbackQuery, state: FSMContext):
    """
    Запускает процесс добавления новой категории.
    Просит ввести название новой категории.
    """
    cur_state = await state.get_state()
    cur_data = await state.get_data()
    await state.update_data(
        draft_state=cur_state,
        draft_data=cur_data
    )
    msg = await callback.message.edit_text("Введите название новой категории:",
                                     reply_markup=back_menu())
    await state.update_data(main_message_id=msg.message_id)
    await state.set_state(CategoryStates.adding)
    await callback.answer()

@router.message(CategoryStates.adding)
@admin_only
async def add_category_name(message: Message, state: FSMContext):
    """
    Обрабатывает название новой категории, сохраняет её в базу.
    """
    await delete_request_and_user_message(message, state)
    name = message.text.strip()
    if not name:
        await message.answer("Название не может быть пустым. Попробуйте снова.")
        return
    category = await create_category(name=name)
    text = f"Категория «{name}» добавлена ✅"
    data = await state.get_data()
    draft_state = data.get('draft_state')
    draft_data = data.get('draft_data', {})
    if draft_state:
        draft_data['category_id'] = category.id
        await state.set_state(draft_state)
        await state.update_data(**draft_data)
        await add_product_category(message, state)
        return
    else:
        await message.answer(text, reply_markup=back_menu())
        await state.clear()



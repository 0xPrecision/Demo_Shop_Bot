from decimal import Decimal
from typing import Union

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from database.crud import create_product, get_category_by_name
from bot.keyboards.admin.catalog_keyboards import create_or_cancel_product_kb, back_menu
from bot.states.admin_states.product_states import AddProductStates
from database.models import Category
from .admin_access import admin_only
from ...utils.admin_utils.catalog_utils import filter_or_change_pr_category
from ...utils.common_utils import delete_request_and_user_message, format_price


router = Router()


@router.callback_query(F.data == "admin_add_product")
@admin_only
async def start_add_product(callback: CallbackQuery, state: FSMContext):
    """
    Запуск FSM добавления товара (шаг 1: название).
    """
    msg = await callback.message.edit_text("Введите название товара:", reply_markup=back_menu())
    await state.set_state(AddProductStates.waiting_name)
    await state.update_data(main_message_id=msg.message_id)
    await callback.answer()


@router.message(AddProductStates.waiting_name)
@admin_only
async def add_product_name(message: Message, state: FSMContext):
    """
    Шаг 1. Получение названия товара.
    """
    await delete_request_and_user_message(message, state)
    name = message.text.strip()
    if not name:
        await delete_request_and_user_message(message, state)
        msg = await message.answer("Название не может быть пустым. Введите ещё раз:")
        await state.update_data(main_message_id=msg.message_id)
        return
    await state.update_data(name=name)
    msg = await message.answer("Введите цену товара (только число):", reply_markup=back_menu())
    await state.update_data(main_message_id=msg.message_id)
    await state.set_state(AddProductStates.waiting_price)


@router.message(AddProductStates.waiting_price)
@admin_only
async def add_product_price(message: Message, state: FSMContext):
    """
    Шаг 2. Получение цены товара.
    """
    await delete_request_and_user_message(message, state)
    price_text = message.text.replace(",", ".").strip()
    try:
        price = float(price_text)
        if price <= 0:
            raise ValueError
    except ValueError:
        msg = await message.answer("Некорректная цена. Введите только положительное число:")
        await state.update_data(main_message_id=msg.message_id)
        return
    await state.update_data(price=price)
    msg = await message.answer("Введите описание товара (или '-' чтобы пропустить):",
                         reply_markup=back_menu())
    await state.update_data(main_message_id=msg.message_id)
    await state.set_state(AddProductStates.waiting_description)


@router.message(AddProductStates.waiting_description)
@admin_only
async def add_product_description(message: Message, state: FSMContext):
    """
    Шаг 3. Получение описания товара.
    """
    await delete_request_and_user_message(message, state)
    description = message.text.strip()
    if description == "-":
        description = ""
    await state.update_data(description=description)
    msg = await message.answer("Введите количество товара:",
                               reply_markup=back_menu())
    await state.update_data(main_message_id=msg.message_id)
    await state.set_state(AddProductStates.waiting_stock)


@router.message(AddProductStates.waiting_stock)
@admin_only
async def add_product_stock(message: Message, state: FSMContext):
    """
    Шаг 4. Получение остатка товара.
    """
    await delete_request_and_user_message(message, state)
    try:
        stock = int(message.text)
        if stock < 0:
            raise ValueError
    except ValueError:
        msg = await message.answer("Некорректный остаток. Введите целое неотрицательное число:")
        await state.update_data(main_message_id=msg.message_id)
        return
    await state.update_data(stock=stock)
    msg = await message.answer("Отправьте фото товара (или '-' чтобы пропустить):",
                         reply_markup=back_menu())
    await state.update_data(main_message_id=msg.message_id)
    await state.set_state(AddProductStates.waiting_photo)


@router.message(AddProductStates.waiting_photo, F.photo)
@admin_only
async def add_product_photo(message: Message, state: FSMContext):
    """
    Шаг 5. Получение фото товара.
    """
    await delete_request_and_user_message(message, state)
    photo = message.photo[-1].file_id  # Берём максимальное качество
    await state.update_data(photo=photo)
    text = "Выберите категорию для товара:"
    await filter_or_change_pr_category(message, state, text)
    await state.set_state(AddProductStates.waiting_category)


@router.message(AddProductStates.waiting_photo)
@admin_only
async def add_product_photo_skip(message: Message, state: FSMContext):
    """
    Шаг 5. Пропуск добавления фото.
    """
    await delete_request_and_user_message(message, state)
    if message.text.strip() != "-":
        msg = await message.answer("Пожалуйста, отправьте фото товара или введите '-' для пропуска.")
        await state.update_data(main_message_id=msg.message_id)
        return

    await state.update_data(photo=None)
    text = "Выберите категорию для товара:"
    await filter_or_change_pr_category(message, state, text)
    await state.set_state(AddProductStates.waiting_category)


@router.callback_query(F.data.startswith("admin_edit_category:"))
@admin_only
async def admin_edit_category(callback: CallbackQuery, state: FSMContext):
    """
    Показывает клавиатуру для смены категории выбранного товара.
    """
    product_id = int(callback.data.split(":")[1])
    text = "Выберите новую категорию для товара:"
    await filter_or_change_pr_category(callback, state, text, product_id)
    await callback.answer()


@router.callback_query(AddProductStates.waiting_category)
@router.message(AddProductStates.waiting_category)
@admin_only
async def add_product_category(event: Union[CallbackQuery, Message], state: FSMContext):
    """
    Шаг 6. Получение категории товара и финальное подтверждение.
    """
    if isinstance(event, CallbackQuery):
        await delete_request_and_user_message(event.message, state)
    else:
        await delete_request_and_user_message(event, state)
    data = await state.get_data()
    category_id = data.get('category_id')
    if category_id:
        category = await Category.get(id=category_id)
        if isinstance(event, CallbackQuery):
            message_obj = event.message
        else:
            message_obj = event

    elif isinstance(event, CallbackQuery):
        if event.data.startswith("change_category:"):
            category_id = int(event.data.split(":", 1)[1])
            category = await Category.get(id=category_id)

        else:
            await event.answer("Ошибка. Некорректная категория.", show_alert=True)
            return
        await event.answer()
        message_obj = event.message

    elif isinstance(event, Message):
        name = event.text.strip()
        category = await get_category_by_name(name)
        category_id = category.id
        message_obj = event

    else:
        return

    await state.update_data(category_id=category_id)
    text = (
        f"<b>Проверьте данные товара:</b>\n\n"
        f"Название: <b>{data.get('name')}</b>\n"
        f"Цена: <b>{format_price(data.get('price'))}</b>₽\n"
        f"Описание: {data.get('description') or '-'}\n"
        f"Остаток: <b>{data.get('stock')}</b>\n"
        f"Категория: <b>{category}</b>\n"
        f"Фото: {'✅' if data.get('photo') else '-'}\n\n"
        f"Создать этот товар?"
    )
    await message_obj.answer(text, reply_markup=create_or_cancel_product_kb())
    await state.set_state(AddProductStates.confirming)


@router.callback_query(AddProductStates.confirming, F.data == "admin_create_product")
@admin_only
async def confirm_create_product(callback: CallbackQuery, state: FSMContext):
    """
    Финальный шаг — создание товара в базе.
    """
    data = await state.get_data()
    category = await Category.get(id=data['category_id'])
    await create_product(
        name=data['name'],
        description=data['description'],
        price=Decimal(data['price']),
        stock=data['stock'],
        category=category,
        photo=data['photo'],
        is_active=True
    )
    await callback.message.edit_text("Товар успешно создан ✅", reply_markup=back_menu())
    await state.clear()
    await callback.answer()
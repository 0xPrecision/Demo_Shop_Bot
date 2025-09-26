from decimal import Decimal
from typing import Union

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.admin.catalog_keyboards import (
    admin_ask_new_product,
    back_menu,
    create_or_cancel_product_kb,
)
from bot.states.admin_states.product_states import AddProductStates
from database.crud import create_product, get_category_by_name
from database.models import Category

from ...utils.admin_utils.catalog_utils import filter_or_change_pr_category
from ...utils.common_utils import delete_request_and_user_message, format_price
from .admin_access import admin_only

router = Router()


@router.callback_query(F.data == "admin_add_product")
@admin_only
async def start_add_product(callback: CallbackQuery, t, state: FSMContext, **_):
    """
    Start the FSM for adding a product (step 1: name).
    """
    msg = await callback.message.edit_text(
        t("add_product.messages.vvedite-nazvanie-tovara"), reply_markup=back_menu(t)
    )
    await state.set_state(AddProductStates.waiting_name)
    await state.update_data(main_message_id=msg.message_id)
    await callback.answer()


@router.message(AddProductStates.waiting_name)
@admin_only
async def add_product_name(message: Message, t, state: FSMContext, **_):
    """
    Step 1. Get the product name.
    """
    await delete_request_and_user_message(message, state)
    name = message.text.strip()
    if not name:
        await delete_request_and_user_message(message, state)
        msg = await message.answer(t("add_product.messages.nazvanie-ne-mozhet-byt"))
        await state.update_data(main_message_id=msg.message_id)
        return
    await state.update_data(name=name)
    msg = await message.answer(
        t("add_product.messages.vvedite-cenu-tovara-tolko"), reply_markup=back_menu(t)
    )
    await state.update_data(main_message_id=msg.message_id)
    await state.set_state(AddProductStates.waiting_price)


@router.message(AddProductStates.waiting_price)
@admin_only
async def add_product_price(message: Message, t, state: FSMContext, **_):
    """
    Step 2. Get the product price.
    """
    await delete_request_and_user_message(message, state)
    price_text = message.text.replace(",", ".").strip()
    try:
        price = float(price_text)
        if price <= 0:
            raise ValueError
    except ValueError:
        msg = await message.answer(
            t("add_product.messages.nekorrektnaya-cena-vvedite-tolko")
        )
        await state.update_data(main_message_id=msg.message_id)
        return
    await state.update_data(price=price)
    msg = await message.answer(
        t("add_product.messages.vvedite-opisanie-tovara-ili"), reply_markup=back_menu(t)
    )
    await state.update_data(main_message_id=msg.message_id)
    await state.set_state(AddProductStates.waiting_description)


@router.message(AddProductStates.waiting_description)
@admin_only
async def add_product_description(message: Message, t, state: FSMContext, **_):
    """
    Step 3. Get the product description.
    """
    await delete_request_and_user_message(message, state)
    description = message.text.strip()
    if description == "-":
        description = ""
    await state.update_data(description=description)
    msg = await message.answer(
        t("add_product.messages.vvedite-kolichestvo-tovara"), reply_markup=back_menu(t)
    )
    await state.update_data(main_message_id=msg.message_id)
    await state.set_state(AddProductStates.waiting_stock)


@router.message(AddProductStates.waiting_stock)
@admin_only
async def add_product_stock(message: Message, t, state: FSMContext, **_):
    """
    Step 4. Get the product stock.
    """
    await delete_request_and_user_message(message, state)
    try:
        stock = int(message.text)
        if stock < 0:
            raise ValueError
    except ValueError:
        msg = await message.answer(
            t("add_product.messages.nekorrektnyj-ostatok-vvedite-celoe")
        )
        await state.update_data(main_message_id=msg.message_id)
        return
    await state.update_data(stock=stock)
    msg = await message.answer(
        t("add_product.messages.otpravte-foto-tovara-ili"), reply_markup=back_menu(t)
    )
    await state.update_data(main_message_id=msg.message_id)
    await state.set_state(AddProductStates.waiting_photo)


@router.message(AddProductStates.waiting_photo, F.photo)
@admin_only
async def add_product_photo(message: Message, state: FSMContext, t):
    """
    Step 5. Get the product photo.
    """
    await delete_request_and_user_message(message, state)
    photo = message.photo[-1].file_id
    await state.update_data(photo=photo)
    text = t("vyberete-kategoriu-tovara")
    await filter_or_change_pr_category(message, state, t, text)
    await state.set_state(AddProductStates.waiting_category)


@router.message(AddProductStates.waiting_photo)
@admin_only
async def add_product_photo_skip(message: Message, t, state: FSMContext, **_):
    """
    Step 5. Skip adding a photo.
    """
    await delete_request_and_user_message(message, state)
    if message.text.strip() != "-":
        msg = await message.answer(t("add_product.messages.otpravte-foto-tovara-ili.2"))
        await state.update_data(main_message_id=msg.message_id)
        return
    await state.update_data(photo=None)
    text = t("vyberete-kategoriu-tovara")
    await filter_or_change_pr_category(message, state, t, text)
    await state.set_state(AddProductStates.waiting_category)


@router.callback_query(F.data.startswith("admin_edit_category:"))
@admin_only
async def admin_edit_category(callback: CallbackQuery, state: FSMContext, t):
    """
    Displays a keyboard for changing the category of the selected product.
    """
    product_id = int(callback.data.split(":")[1])
    text = t("vyberete-novuyu-kategoriu-tovara")
    await filter_or_change_pr_category(callback, state, t, text, product_id)
    await callback.answer()


@router.callback_query(AddProductStates.waiting_category)
@router.message(AddProductStates.waiting_category)
@admin_only
async def add_product_category(
    event: Union[CallbackQuery, Message], state: FSMContext, t, **_
):
    """
    Step 6. Get the product category and perform the final confirmation.
    """
    if isinstance(event, CallbackQuery):
        await delete_request_and_user_message(event.message, state)
    else:
        await delete_request_and_user_message(event, state)
    data = await state.get_data()
    category_id = data.get("category_id")
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
            await event.answer(
                t("add_product.messages.nekorrektnaya-kategoriya"), show_alert=True
            )
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

    name = data.get("name")
    price = format_price(data.get("price"))
    descr = data.get("description") if data.get("description") else "-"
    stock = data.get("stock")
    img = "✅" if data.get("photo") else "-"

    text = t("add_product.dannye-tovara").format(
        name=name,
        price=price,
        currency=t("currency"),
        descr=descr,
        stock=stock,
        category=category,
        img=img,
    )

    await message_obj.answer(text, reply_markup=create_or_cancel_product_kb(t))
    await state.set_state(AddProductStates.confirming)


@router.callback_query(AddProductStates.confirming, F.data == "admin_create_product")
@admin_only
async def confirm_create_product(callback: CallbackQuery, t, state: FSMContext, **_):
    """
    Final step — create the product in the database.
    """
    data = await state.get_data()
    category = await Category.get(id=data["category_id"])
    await create_product(
        name=data["name"],
        description=data["description"],
        price=Decimal(data["price"]),
        stock=data["stock"],
        category=category,
        photo=data["photo"],
        is_active=True,
    )
    await callback.message.edit_text(
        t("add_product.messages.tovar-uspeshno-sozdan"),
        reply_markup=admin_ask_new_product(t),
    )
    await state.clear()
    await callback.answer()

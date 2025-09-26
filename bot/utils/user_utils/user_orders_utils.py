from decimal import Decimal
from typing import Dict, Optional

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.keyboards.user.order_keyboards import (
    order_confirm_keyboard,
    order_details_keyboard,
    show_orders_keyboard,
)
from bot.keyboards.user.user_profile_keyboards import profile_orders_keyboard
from bot.states.user_states.order_states import OrderStates
from bot.utils.common_utils import (
    delete_request_and_user_message,
    format_price,
    format_product_name,
)
from database.crud import get_cart, get_order_by_id, get_order_items, get_orders


async def show_orders_menu(
    callback: CallbackQuery,
    t,
    state: FSMContext,
    msg_text: str,
    order_status: Optional[list | str] = None,
) -> None:
    """
    Displays the user's orders menu with optional status filter.
    """
    await delete_request_and_user_message(callback.message, state)

    user_id = callback.from_user.id
    orders = await get_orders(user_id)

    if not orders:
        await callback.message.answer(msg_text, reply_markup=profile_orders_keyboard(t))
        return

    # нормализуем фильтр: None -> все; str -> {str}; iterable -> set(...)
    if order_status is None:
        allowed = None
    elif isinstance(order_status, str):
        allowed = {order_status}
    else:
        allowed = set(order_status)

    filtered = [o for o in orders if allowed is None or o.status in allowed]

    if not filtered:
        await callback.message.answer(msg_text, reply_markup=profile_orders_keyboard(t))
        return

    filtered.sort(key=lambda x: x.created_at, reverse=True)

    text = t("orders.list.header").format(separator="-" * 19)
    for order in filtered:
        text += t("orders.list.items").format(
            id=order.id,
            date=order.created_at.strftime(t("date_format")),
            status=order.status,
            total=format_price(order.total_price),
            currency=t("currency"),
        )
    text += t("orders.list.footer").format(separator="-" * 19)

    await callback.message.answer(text, reply_markup=show_orders_keyboard(filtered, t))


async def get_order_details(order_id: int, t, **_) -> Dict:
    """
    Get detailed order information by its identifier.

    :param order_id: int — order ID.
    :return: Dict — {"text": description, "keyboard": inline keyboard}.
    """
    order = await get_order_by_id(order_id)
    if not order:
        return {
            "text": t("admin_orders.messages.zakaz-ne-najden"),
            "keyboard": order_details_keyboard(t, order_id),
        }
    order_items = await get_order_items(order)
    total = sum([item.quantity * float(item.product.price) for item in order_items])
    items_text = "\n".join(
        [
            f'• {format_product_name(item.product.name)} — {item.quantity} x {format_price(item.product.price)} {t("currency")} = {format_price(item.quantity * float(item.product.price))} {t("currency")}'
            for item in order_items
        ]
    )

    text = t("user_orders_utils.misc.b-zakaz-b").format(
        id=order.id,
        created_at=order.created_at.strftime(t("date_format")),
        status=order.status,
        items_text=items_text,
        payment=order.payment_method or "-",
        delivery=order.delivery_method or "-",
        address=order.address or "-",
        items=items_text,
        total=format_price(total),
        currency=t("currency"),
    )

    return {"text": text, "keyboard": order_details_keyboard(t, order.id)}


async def show_order_summary(message_or_callback, state: FSMContext, t) -> None:
    """
    Displays the order summary to the user with all entered data (supports Cart ORM and dict).
    Provides options to confirm the order or edit the data.
    """
    await delete_request_and_user_message(message_or_callback, state)
    user_id = message_or_callback.from_user.id
    data = await state.get_data()
    cart_items = await get_cart(user_id)
    client = data.get("name") or "-"
    phone = data.get("phone") or "-"
    pay = data.get("payment_method") or "-"
    delivery = data.get("delivery_method") or "-"
    address = data.get("address") or t("checkout.summary.no_address")
    comment = data.get("comment") or "-"

    summary = t("checkout.summary.header").format(
        name=client,
        phone=phone,
        delivery=delivery,
        address=address,
        comment=comment,
        payment=pay,
    )

    total = Decimal("0")
    for item in cart_items:
        name = format_product_name(item.product.name)
        qty = item.quantity
        price = Decimal(item.product.price)
        pr_sum = price * qty
        total += pr_sum
        summary += t("checkout.summary.item_line").format(
            name=name, qty=qty, line_total=format_price(pr_sum), currency=t("currency")
        )

    summary += t("checkout.summary.total_block").format(
        total=format_price(total), currency=t("currency")
    )

    summary += t("checkout.summary.hint")

    if hasattr(message_or_callback, "edit_text"):
        await message_or_callback.answer(
            summary, reply_markup=order_confirm_keyboard(t)
        )
    else:
        await message_or_callback.message.answer(
            summary, reply_markup=order_confirm_keyboard(t)
        )
    await state.set_state(OrderStates.confirm)

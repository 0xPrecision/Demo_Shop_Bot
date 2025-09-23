from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.utils.user_utils.user_orders_utils import show_orders_menu, get_order_details


router = Router()


@router.callback_query(F.data == 'menu_orders')
async def show_history_orders_menu(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Handler for displaying the user's orders menu.
	"""
    text = "У вас пока нет заказов."
    await show_orders_menu(callback, state, text)
    await callback.answer()

@router.callback_query(F.data == "active_orders")
async def show_active_orders_menu(callback: CallbackQuery, state: FSMContext):
    text = "У вас нет текущих заказов."
    await show_orders_menu(callback, state, text, order_status='В работе')
    await callback.answer()

@router.callback_query(F.data.startswith("order_details_"))
async def show_order_details(callback: CallbackQuery):
    order_id = int(callback.data.split("_")[2])
    details = await get_order_details(order_id)
    await callback.message.edit_text(details["text"], reply_markup=details["keyboard"])


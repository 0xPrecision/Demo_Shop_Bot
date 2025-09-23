from typing import List, Tuple
from decimal import Decimal
from aiogram.types import InlineKeyboardMarkup
from database.models import Cart, Product
from bot.utils.common_utils import paginate, format_price
from bot.keyboards.user.user_common_keyboards import cart_back_menu
from bot.keyboards.user.user_cart_keyboards import cart_keyboard


PAGE_SIZE = 5


async def build_cart_view(
    cart_items: List[Cart],
    page: int = 0
) -> Tuple[str, InlineKeyboardMarkup]:
    """
    Builds text and a keyboard for displaying the user's cart with pagination.
    Shows the full cart in the text, but only products for the current page in inline buttons.
    
    :param cart_items: List of the user's Cart objects.
    :param page: Page number (from 0).
    :return: Tuple (message text, inline keyboard).
	"""
    if cart_items:
        # Загружаем все товары одной выборкой и делаем словарь {id: Product}
        product_ids = [item.product_id for item in cart_items]
        products = await Product.filter(id__in=product_ids).all()
        products_dict = {p.id: p for p in products}
        # Считаем итог, формируем пары (Cart, Product)
        cart_pairs = []
        total = 0
        for item in cart_items:
            product = products_dict.get(item.product_id)
            if product:
                amount = item.quantity * Decimal(product.price)
                total += amount
                cart_pairs.append((item, product))

        total_items = len(cart_pairs)
        total_pages = max(1, (total_items + PAGE_SIZE - 1) // PAGE_SIZE)
        if page > 0 and page >= total_pages:
            page = total_pages - 1
        # Формируем текст всей корзины

        text = "🛒 <b>Ваша корзина</b>\n\n"
        for item, product in cart_pairs:
            product_price = product.price * item.quantity
            text += f"<b>{product.name}</b>\n"
            text += f"  └ {item.quantity} × {format_price(product.price)} ₽ = {format_price(product_price)} ₽\n"

        text += f"\n<b>Итого:</b> <u>{format_price(total)} ₽</u>"
        page_products, total_pages, _ = paginate(cart_pairs, page, PAGE_SIZE)
        keyboard = cart_keyboard(page_products, page, total_pages)

        return text, keyboard
    else:
        return "🧹 Ваша корзина пуста.", cart_back_menu()

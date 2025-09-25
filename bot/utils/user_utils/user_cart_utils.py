from typing import List, Tuple
from decimal import Decimal
from aiogram.types import InlineKeyboardMarkup
from database.models import Cart, Product
from bot.utils.common_utils import paginate, format_price
from bot.keyboards.user.user_common_keyboards import cart_back_menu
from bot.keyboards.user.user_cart_keyboards import cart_keyboard
PAGE_SIZE = 5

async def build_cart_view(cart_items: List[Cart], t, page: int=0, **_) -> Tuple[str, InlineKeyboardMarkup]:
    """
    Builds text and a keyboard for displaying the user's cart with pagination.
    Shows the full cart in the text, but only products for the current page in inline buttons.
    
    :param cart_items: List of the user's Cart objects.
    :param page: Page number (from 0).
    :return: Tuple (message text, inline keyboard).
	"""
    if cart_items:
        product_ids = [item.product_id for item in cart_items]
        products = await Product.filter(id__in=product_ids).all()
        products_dict = {p.id: p for p in products}
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
        text = t('user_cart_utils.misc.b-vasha-korzina-b')
        for item, product in cart_pairs:
            product_price = product.price * item.quantity
            text += t("cart.item_line").format(
                name=product.name,
                qty=item.quantity,
                unit_price=format_price(product.price),
                total=format_price(product_price)
            )
        text += t("cart.total").format(total=format_price(total))
        page_products, total_pages, _ = paginate(cart_pairs, page, PAGE_SIZE)
        keyboard = cart_keyboard(page_products, page, total_pages, t)
        return text, keyboard
    else:
        return t('user_cart.messages.vasha-korzina-pusta'), cart_back_menu(t)
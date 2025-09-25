from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.utils.common_utils import format_price, format_product_name

def show_categories_keyboard(categories: list[str], t, **_) -> InlineKeyboardMarkup:
    """
    Builds a keyboard for selecting a product category.
    
    :param categories: List of category names.
    :return: InlineKeyboardMarkup with a button for each category and a “Main Menu” button.
	"""
    keyboard = [[InlineKeyboardButton(text=cat, callback_data=f'category_{cat}')] for cat in categories]
    keyboard.append([InlineKeyboardButton(text=t('order_keyboards.buttons.v-glavnoe-menyu'), callback_data='menu_main')])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def show_product_info_kb(product_id: int, source: str, t, category_name: str=None, page: int=None, **_) -> InlineKeyboardMarkup:
    """
    Builds an inline keyboard for product details.
    
    :param product_id: Product ID.
    :param source: Source from which the product card was opened ('catalog' or 'cart').
    :param category_name: Category name for return.
    :param page: Page number for return.
    :return: InlineKeyboardMarkup.
	"""
    if source == 'catalog':
        back_callback = f'category_{category_name}_{page}'
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t('user_catalog_keyboards.buttons.v-korzinu'), callback_data=f'addtocart_{product_id}')], [InlineKeyboardButton(text=t('catalog_keyboards.buttons.nazad'), callback_data=back_callback)]])
    else:
        back_callback = 'menu_cart'
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t('user_catalog_keyboards.buttons.ubrat-iz-korziny'), callback_data=f'removefromcart_{product_id}')], [InlineKeyboardButton(text=t('catalog_keyboards.buttons.nazad'), callback_data=back_callback)]])
    return kb

def products_keyboard(products: list[dict], category: str, page: int, total_pages: int, t, **_) -> InlineKeyboardMarkup:
    """
    Creates an inline keyboard for displaying products with pagination.
    
    :param products: List of products on the current page.
    :param category: Current category.
    :param page: Current page number (from 0).
    :param total_pages: Total number of pages.
    :return: InlineKeyboardMarkup with products and navigation.
	"""
    page_label = t("user_catalog.page_label").format(page=page + 1, total_pages=total_pages)

    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton(text="⬅️", callback_data=f"category_{category}_{page - 1}"))

        nav_row.append(InlineKeyboardButton(text=page_label, callback_data="noop"))

    if page < total_pages - 1:
        nav_row.append(InlineKeyboardButton(text="➡️", callback_data=f"category_{category}_{page + 1}"))

    rows = [
        [
            InlineKeyboardButton(
                text=f"{format_product_name(product.name, 70)}",
                callback_data=f"product_{product.id}_catalog_{category}_{page}",
            ),
            InlineKeyboardButton(
                text=f"{format_price(product.price)} {t("currency")}",
                callback_data="noop",
            ),
            InlineKeyboardButton(
                text=t("user_catalog_keyboards.buttons.v-korzinu"),
                callback_data=f"addtocart_{product.id}",
            ),
        ]
        for product in products
    ]

    rows.append([InlineKeyboardButton(text=t("catalog_keyboards.buttons.nazad"), callback_data="menu_catalog")])
    rows.append([InlineKeyboardButton(text=t("user_catalog_keyboards.buttons.korzina"), callback_data="menu_cart")])
    rows.append([InlineKeyboardButton(text=t("order_keyboards.buttons.v-glavnoe-menyu"), callback_data="menu_main")])
    rows.append(nav_row)

    return InlineKeyboardMarkup(inline_keyboard=rows)
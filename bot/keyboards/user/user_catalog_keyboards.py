from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.utils.common_utils import format_price, format_product_name


def show_categories_keyboard(categories: list[str]) -> InlineKeyboardMarkup:
    """
    Формирует клавиатуру для выбора категории товаров.

    :param categories: Список названий категорий.
    :return: Объект InlineKeyboardMarkup с кнопками для каждой категории и кнопкой "В главное меню".
    """
    keyboard = [
        [InlineKeyboardButton(text=cat, callback_data=f"category_{cat}")]
        for cat in categories
    ]
    keyboard.append([InlineKeyboardButton(text="🏠 В главное меню", callback_data="menu_main")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def show_product_info_kb(product_id: int, source: str, category_name: str = None, page: int = None) -> InlineKeyboardMarkup:
    """
    Формирует инлайн-клавиатуру для подробной информации о товаре.

    :param product_id: ID товара.
    :param source: Источник, откуда открыта карточка товара ('catalog' или 'cart').
    :param category_name: Название категории для возврата.
    :param page: Номер страницы для возврата.
    :return: InlineKeyboardMarkup.
    """
    if source == "catalog":
        back_callback = f"category_{category_name}_{page}"
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🛒 В корзину", callback_data=f"addtocart_{product_id}")],
                [InlineKeyboardButton(text="⬅️ Назад", callback_data=back_callback)],
            ]
        )

    else:
        back_callback = "menu_cart"
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🛒 Убрать из корзины", callback_data=f"removefromcart_{product_id}")],
                [InlineKeyboardButton(text="⬅️ Назад", callback_data=back_callback)],
            ]
        )

    return kb


def products_keyboard(products: list[dict], category: str, page: int, total_pages: int) -> InlineKeyboardMarkup:
    """
    Создаёт инлайн-клавиатуру для вывода товаров с навигацией (пагинацией).

    :param products: Список товаров на текущей странице
    :param category: Текущая категория
    :param page: Номер текущей страницы (от 0)
    :param total_pages: Всего страниц
    :return: InlineKeyboardMarkup с товарами и навигацией
    """
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton(
            text="⬅️",
            callback_data=f"category_{category}_{page - 1}"
        ))

        nav_row.append(InlineKeyboardButton(
            text=f"Страница {page + 1}/{total_pages}", callback_data="noop"
        ))

    if page < total_pages - 1:
        nav_row.append(InlineKeyboardButton(
            text="➡️",
            callback_data=f"category_{category}_{page + 1}"
        ))

    keyboard = [
        [
            InlineKeyboardButton(
                text=f"{format_product_name(product.name, 35)} — {format_price(product.price)} ₽",
                callback_data=f"product_{product.id}_catalog_{category}_{page}"
            ),
            InlineKeyboardButton(
                text="🛒 В корзину",
                callback_data=f"addtocart_{product.id}"
            )
        ]
        for product in products
    ]

    keyboard.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data="menu_catalog")
    ])

    keyboard.append([
        InlineKeyboardButton(text="🛒 Корзина", callback_data="menu_cart")
    ])

    keyboard.append([
        InlineKeyboardButton(text="🏠 В главное меню", callback_data="menu_main")
    ])

    if nav_row:
        keyboard.append(nav_row)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
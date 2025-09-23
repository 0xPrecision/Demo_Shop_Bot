from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Tuple

from bot.utils.common_utils import format_price
from database.models import Category


# ============ COMMON_KB ============

def back_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Выйти в главное меню", callback_data="/start_admin")]
    ])

# ============ CATALOG_KB ============

def admin_catalog_menu_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📦 Товары", callback_data="admin_products")],
            [InlineKeyboardButton(text="📂 Категории", callback_data="admin_categories")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="/start_admin")]
        ]
    )

# ============ PRODUCTS_KB ============

def create_or_cancel_product_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Создать", callback_data="admin_create_product")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_products")]
    ])


def ask_of_create_product() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить товар", callback_data="admin_add_product")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="/start_admin")]
    ])


def create_or_cancel_edit_product_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="✅ Сохранить", callback_data="edit_save")],
                [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_products")]
            ]
        )


def confirm_deletion_product(product_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Да, скрыть", callback_data=f"admin_delete_product_yes:{product_id}")],
        [InlineKeyboardButton(text="⬅️ Нет, отмена", callback_data="admin_products")],
    ])


def products_list_keyboard(products: List[Tuple[int, str]], page: int, has_next: bool, has_prev: bool) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=short_info, callback_data=f"admin_product_detail:{prod_id}")]
        for prod_id, short_info in products
    ]
    nav = []
    if has_prev:
        nav.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"admin_products_page:{page-1}"))
    if has_next:
        nav.append(InlineKeyboardButton(text="Вперёд ➡️", callback_data=f"admin_products_page:{page+1}"))
    if nav:
        buttons.append(nav)
    buttons.append([InlineKeyboardButton(text="🔍 Поиск товара", callback_data="admin_search_product")])
    buttons.append([InlineKeyboardButton(text="➕ Добавить товар", callback_data="admin_add_product")])
    buttons.append([InlineKeyboardButton(text="🏠 Выйти в главное меню", callback_data="/start_admin")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def show_products_for_search(products) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=f"#_id {p.id} | {p.name} | {format_price(p.price)} ₽",
                callback_data=f"admin_product_detail:{p.id}"
            )] for p in products
        ]
    )


def back_to_search_keyboard() -> InlineKeyboardMarkup:
    """
    Keyboard for returning to product search.
	"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔍 Повторить попытку", callback_data="admin_search_product")],
            [InlineKeyboardButton(text="⬅️ К товарам", callback_data="admin_products")],
        ]
    )


def product_admin_keyboard(product_id: int) -> InlineKeyboardMarkup:
    """
    Keyboard for editing/deleting a product.
	"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"admin_edit_product:{product_id}")],
            [InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"admin_delete_product:{product_id}")],
            [InlineKeyboardButton(text="⬅️ К товарам", callback_data="admin_products")],
        ]
    )


def product_edit_field_keyboard(product_id: int) -> InlineKeyboardMarkup:
    """
    Keyboard for selecting a product field to edit.
	"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Название", callback_data=f"edit_field:name:{product_id}")],
            [InlineKeyboardButton(text="Цена", callback_data=f"edit_field:price:{product_id}")],
            [InlineKeyboardButton(text="Описание", callback_data=f"edit_field:description:{product_id}")],
            [InlineKeyboardButton(text="Остаток", callback_data=f"edit_field:stock:{product_id}")],
            [InlineKeyboardButton(text="Фото", callback_data=f"edit_field:photo:{product_id}")],
            [InlineKeyboardButton(text="Категория", callback_data=f"edit_field:category:{product_id}")],
            [InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"edit_field:confirm:{product_id}")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_products")],
        ]
    )


def change_category_keyboard(categories: List["Category"]) -> InlineKeyboardMarkup:
    """Клавиатура отображения категорий для товаров в режиме редактирования"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
        [InlineKeyboardButton(text=cat.name, callback_data=f"change_category:{cat.id}")]
        for cat in categories
    ])

# ============ CATEGORIES_KB ============

def ask_of_create_category() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить категорию", callback_data="admin_add_category")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="/start_admin")]
    ])


def show_products_or_edit_category(cat_id) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔧 Редактировать категорию", callback_data=f"admin_edit_category:{cat_id}")],
        [InlineKeyboardButton(text="🗂️ Просмотреть товары", callback_data=f"admin_category_filter:{cat_id}")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=f"admin_categories")]
    ])


def edit_or_deletion_category(cat_id) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔧 Переименовать", callback_data=f"admin_rename_category_select:{cat_id}")],
        [InlineKeyboardButton(text="🗑️️ Удалить", callback_data=f"admin_delete_category_select:{cat_id}")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=f"admin_select_category:{cat_id}")]
    ])


def admin_categories_keyboard(categories: List["Category"]) -> InlineKeyboardMarkup:
    """Клавиатура для отображения категорий"""
    buttons = [
        [InlineKeyboardButton(text=cat.name, callback_data=f"admin_select_category:{cat.id}")]
        for cat in categories
    ]
    buttons.append([InlineKeyboardButton(text="➕ Добавить категорию", callback_data="admin_add_category")])
    buttons.append([InlineKeyboardButton(text="🏠 Выйти в главное меню", callback_data="/start_admin")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def show_categories_to_edit(categories) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=cat.name, callback_data=f"admin_rename_category_select:{cat.id}")]
            for cat in categories
        ]
    )


def show_categories_to_delete(categories) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=cat.name, callback_data=f"admin_delete_category_select:{cat.id}")]
            for cat in categories
        ]
    )


def confirm_deletion_category(cat_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Да, удалить", callback_data=f"admin_delete_category_yes:{cat_id}")],
            [InlineKeyboardButton(text="⬅️ Нет, отмена", callback_data="admin_categories")]
        ]
    )
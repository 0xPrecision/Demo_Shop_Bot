from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Tuple
from bot.utils.common_utils import format_price
from database.crud import get_product_by_id
from database.models import Category


def back_menu(t, **_) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t('catalog_keyboards.buttons.vyjti-v-glavnoe'), callback_data='/start_admin')]])

def admin_ask_new_product(t, **_):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t('catalog_keyboards.buttons.dobavit-noviy-tovar'), callback_data='admin_add_product')], [InlineKeyboardButton(text=t('catalog_keyboards.buttons.k-tovaram'), callback_data='admin_products')]])

def admin_catalog_menu_keyboard(t, **_):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t('catalog_keyboards.buttons.tovary'), callback_data='admin_products')], [InlineKeyboardButton(text=t('catalog_keyboards.buttons.kategorii'), callback_data='admin_categories')], [InlineKeyboardButton(text=t('catalog_keyboards.buttons.nazad'), callback_data='/start_admin')]])

def create_or_cancel_product_kb(t, **_) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t('catalog_keyboards.buttons.sozdat'), callback_data='admin_create_product')], [InlineKeyboardButton(text=t('catalog_keyboards.buttons.otmena'), callback_data='admin_products')]])

def ask_of_create_product(t, **_) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t('catalog_keyboards.buttons.dobavit-tovar'), callback_data='admin_add_product')], [InlineKeyboardButton(text=t('catalog_keyboards.buttons.otmena'), callback_data='/start_admin')]])

def create_or_cancel_edit_product_kb(t, **_) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t('catalog_keyboards.buttons.sohranit'), callback_data='edit_save')], [InlineKeyboardButton(text=t('catalog_keyboards.buttons.otmena'), callback_data='admin_products')]])

def confirm_deletion_product(product_id: int, t, **_) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t('catalog_keyboards.buttons.da-skryt'), callback_data=f'admin_delete_product_yes:{product_id}')], [InlineKeyboardButton(text=t('catalog_keyboards.buttons.net-otmena'), callback_data='admin_products')]])

def products_list_keyboard(products: List[Tuple[int, str]], page: int, has_next: bool, has_prev: bool, t, **_) -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(text=short_info, callback_data=f'admin_product_detail:{prod_id}')] for prod_id, short_info in products]
    nav = []
    if has_prev:
        nav.append(InlineKeyboardButton(text=t('catalog_keyboards.buttons.nazad'), callback_data=f'admin_products_page:{page - 1}'))
    if has_next:
        nav.append(InlineKeyboardButton(text=t('catalog_keyboards.buttons.vpered'), callback_data=f'admin_products_page:{page + 1}'))
    if nav:
        buttons.append(nav)
    buttons.append([InlineKeyboardButton(text=t('catalog_keyboards.buttons.poisk-tovara'), callback_data='admin_search_product')])
    buttons.append([InlineKeyboardButton(text=t('catalog_keyboards.buttons.dobavit-tovar'), callback_data='admin_add_product')])
    buttons.append([InlineKeyboardButton(text=t('catalog_keyboards.buttons.vyjti-v-glavnoe'), callback_data='/start_admin')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def show_products_for_search(products, t) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text=f"#_id {p.id} | {p.name} | {format_price(p.price)} ₽ | {p.status_label(t)}",
                callback_data=f"admin_product_detail:{p.id}"
            )
        ]
        for p in products
    ]

    keyboard.append(
        [
            InlineKeyboardButton(
                text=t("catalog_keyboards.buttons.nazad"),
                callback_data="admin_products"
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def back_to_search_keyboard(t, **_) -> InlineKeyboardMarkup:
    """
    Keyboard for returning to product search.
	"""
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t('catalog_keyboards.buttons.povtorit-popytku'), callback_data='admin_search_product')], [InlineKeyboardButton(text=t('catalog_keyboards.buttons.k-tovaram'), callback_data='admin_products')]])

async def product_admin_keyboard(product_id: int, t, **_) -> InlineKeyboardMarkup:
    """
    Keyboard for editing and deleting/restoring a product.
    Покажи delete, если товар активен; restore — если в архиве.
    """
    rows = [
        [InlineKeyboardButton(text=t("catalog_keyboards.buttons.redaktirovat"),
                              callback_data=f"admin_edit_product:{product_id}")]
    ]

    product = await get_product_by_id(product_id)
    is_active = product.is_active

    if is_active:
        rows.append([InlineKeyboardButton(text=t("catalog_keyboards.buttons.udalit"),
                                          callback_data=f"admin_delete_product:{product_id}")])
    else:
        rows.append([InlineKeyboardButton(text=t("catalog_keyboards.buttons.vosstanovit"),
                                          callback_data=f"admin_restore_product:{product_id}")])

    rows.append([InlineKeyboardButton(text=t("catalog_keyboards.buttons.k-tovaram"),
                                      callback_data="admin_products")])

    return InlineKeyboardMarkup(inline_keyboard=rows)

def product_edit_field_keyboard(product_id: int, t, **_) -> InlineKeyboardMarkup:
    """
    Keyboard for selecting a product field to edit.
	"""
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t('catalog_keyboards.buttons.nazvanie'), callback_data=f'edit_field:name:{product_id}')], [InlineKeyboardButton(text=t('catalog_keyboards.buttons.kategoriya'), callback_data=f'edit_field:category:{product_id}')], [InlineKeyboardButton(text=t('catalog_keyboards.buttons.opisanie'), callback_data=f'edit_field:description:{product_id}')], [InlineKeyboardButton(text=t('catalog_keyboards.buttons.cena'), callback_data=f'edit_field:price:{product_id}')], [InlineKeyboardButton(text=t('catalog_keyboards.buttons.ostatok'), callback_data=f'edit_field:stock:{product_id}')], [InlineKeyboardButton(text=t('catalog_keyboards.buttons.foto'), callback_data=f'edit_field:photo:{product_id}')], [InlineKeyboardButton(text=t('catalog_keyboards.buttons.podtverdit'), callback_data=f'edit_field:confirm:{product_id}')], [InlineKeyboardButton(text=t('catalog_keyboards.buttons.otmena'), callback_data='admin_products')]])

def change_category_keyboard(categories: List['Category']) -> InlineKeyboardMarkup:
    """Клавиатура отображения категорий для товаров в режиме редактирования"""
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=cat.name, callback_data=f'change_category:{cat.id}')] for cat in categories])

def ask_of_create_category(t, **_) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t('catalog_keyboards.buttons.dobavit-kategoriyu'), callback_data='admin_add_category')], [InlineKeyboardButton(text=t('catalog_keyboards.buttons.otmena'), callback_data='/start_admin')]])

def show_products_or_edit_category(cat_id, t, **_) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t('catalog_keyboards.buttons.redaktirovat-kategoriyu'), callback_data=f'admin_edit_category:{cat_id}')], [InlineKeyboardButton(text=t('catalog_keyboards.buttons.prosmotret-tovary'), callback_data=f'admin_category_filter:{cat_id}')], [InlineKeyboardButton(text=t('catalog_keyboards.buttons.nazad'), callback_data=f'admin_categories')]])

def edit_or_deletion_category(cat_id, t, **_) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t('catalog_keyboards.buttons.pereimenovat'), callback_data=f'admin_rename_category_select:{cat_id}')], [InlineKeyboardButton(text=t('catalog_keyboards.buttons.udalit.2'), callback_data=f'admin_delete_category_select:{cat_id}')], [InlineKeyboardButton(text=t('catalog_keyboards.buttons.nazad'), callback_data=f'admin_select_category:{cat_id}')]])

def admin_categories_keyboard(categories: List['Category'], t, **_) -> InlineKeyboardMarkup:
    """Клавиатура для отображения категорий"""
    buttons = [[InlineKeyboardButton(text=cat.name, callback_data=f'admin_select_category:{cat.id}')] for cat in categories]
    buttons.append([InlineKeyboardButton(text=t('catalog_keyboards.buttons.dobavit-kategoriyu'), callback_data='admin_add_category')])
    buttons.append([InlineKeyboardButton(text=t('catalog_keyboards.buttons.vyjti-v-glavnoe'), callback_data='/start_admin')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def show_categories_to_edit(categories) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=cat.name, callback_data=f'admin_rename_category_select:{cat.id}')] for cat in categories])

def show_categories_to_delete(categories) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=cat.name, callback_data=f'admin_delete_category_select:{cat.id}')] for cat in categories])

def confirm_deletion_category(cat_id: int, t, **_) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t('catalog_keyboards.buttons.da-udalit'), callback_data=f'admin_delete_category_yes:{cat_id}')], [InlineKeyboardButton(text=t('catalog_keyboards.buttons.net-otmena'), callback_data='admin_categories')]])
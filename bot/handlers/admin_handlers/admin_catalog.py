from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from bot.keyboards.admin.catalog_keyboards import product_admin_keyboard, admin_catalog_menu_keyboard, show_products_or_edit_category
from database.models import Category
from ...utils.admin_utils.catalog_utils import get_products_info, filter_or_change_pr_category
from database.crud import get_products_page, get_product_by_id, get_products_page_by_category
from .admin_access import admin_only
from ...utils.common_utils import format_price, delete_request_and_user_message

router = Router()


@router.callback_query(F.data == "admin_catalog")
@admin_only
async def admin_catalog_menu(callback: CallbackQuery):
    """
    Главное меню каталога: выбор между товарами и категориями.
    """
    await callback.message.edit_text(
        "Что вы хотите просмотреть/редактировать?",
        reply_markup=admin_catalog_menu_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "admin_products")
@admin_only
async def admin_products_list(callback: CallbackQuery, state: FSMContext):
    """
    Показывает первую страницу товаров.
    """
    await delete_request_and_user_message(callback.message, state)
    page = 1
    text = "🛒 <b>Список товаров</b> (выберите для просмотра/редактирования):"
    func = get_products_page(page)
    await get_products_info(callback, page, text, func, state)
    await callback.answer()


@router.callback_query(F.data == "admin_categories")
@admin_only
async def admin_categories_entry(callback: CallbackQuery, state: FSMContext):
    """
    Показывает инлайн-клавиатуру для выбора категории товаров (фильтр).
    """
    text = "Категории товаров (выберите для просмотра/редактирования):"
    await filter_or_change_pr_category(callback, state, text)
    await callback.answer()


@router.callback_query(F.data.startswith("admin_products_page:"))
@admin_only
async def admin_products_page(callback: CallbackQuery, state: FSMContext):
    """
    Перелистывание страниц каталога товаров.
    """
    page = int(callback.data.split(":")[1])
    text = f"🛒 <b>Товары</b> (стр. {page}):"
    func = get_products_page(page)
    await get_products_info(callback, page, text, func, state)
    await callback.answer()


@router.callback_query(F.data.startswith("admin_product_detail:"))
@admin_only
async def admin_product_detail(callback: CallbackQuery, state: FSMContext):
    """
    Показывает детали товара и клавиатуру для админа.
    """
    product_id = int(callback.data.split(":")[1])
    product = await get_product_by_id(product_id)
    await product.fetch_related("category")

    if not product:
        await callback.answer("Товар не найден.", show_alert=True)
        return
    text = (f"<b>Товар:</b>\n"
            f"<b>{product.name}</b>\n"
            f"Остаток: {product.stock}\n"
            f"Категория: {product.category.name if product.category else '—'}\n"
            f"Цена: {format_price(product.price)}₽\n"
            f"Описание: {product.description or '—'}")


    if product.photo:
        # Отправляем фото отдельным сообщением
        msg = await callback.message.answer_photo(
            photo=product.photo,
            caption=text,
            reply_markup=product_admin_keyboard(product_id),
        )
        await callback.message.delete()
        await state.update_data(main_message_id=msg.message_id)
    else:
        msg = await callback.message.edit_text(
            text=text,
            reply_markup=product_admin_keyboard(product_id)
        )
        await state.update_data(main_message_id=msg.message_id)
    await callback.answer()



@router.callback_query(F.data.startswith("admin_select_category:"))
@admin_only
async def admin_products_by_category(callback: CallbackQuery):
    """Показывает опции выбранной категории"""
    category_id = int(callback.data.split(":", 1)[1])
    await callback.message.edit_text("Выберете действие:",
                                     reply_markup=show_products_or_edit_category(category_id))



@router.callback_query(F.data.startswith("admin_category_filter:"))
@admin_only
async def admin_products_by_category(callback: CallbackQuery, state: FSMContext):
    """
    Показывает товары выбранной категории (фильтр) для админа.
    """
    category_id = int(callback.data.split(":", 1)[1])
    page = 1
    category = await Category.get(id=category_id)
    text = f"🛒 <b>Товары категории: {category.name}</b>"
    func = get_products_page_by_category(category_id, page)
    await get_products_info(callback, page, text, func, state)
    await callback.answer()



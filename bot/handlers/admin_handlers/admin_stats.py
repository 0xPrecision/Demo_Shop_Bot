from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
import csv
import io
from datetime import datetime, timedelta
import tempfile
from .admin_access import admin_only
from database.models import Order, Product, OrderItem
from ...keyboards.admin.stats_kb import stats_actions
router = Router()

@router.callback_query(F.data == 'admin_stats')
@admin_only
async def admin_stats_menu(callback: CallbackQuery):
    """
    Statistics main menu: summary and quick export of orders/products.
	"""
    date_from = datetime.now() - timedelta(days=30)
    orders = await Order.filter(created_at__gte=date_from).all()
    orders_count = len(orders)
    total_sum = sum([float(o.total_price) for o in orders])
    top_products = {}
    for o in orders:
        items = await OrderItem.filter(order=o)
        for it in items:
            key = it.product_id
            top_products[key] = top_products.get(key, 0) + it.quantity
    top_products_sorted = sorted(top_products.items(), key=lambda x: -x[1])
    top_lines = []
    for idx, (prod_id, qty) in enumerate(top_products_sorted[:5], 1):
        prod = await Product.get_or_none(id=prod_id)
        if prod:
            top_lines.append(f'{idx}) {prod.name} — {qty} шт.')
    stats_text = f'📊 <b>Статистика за 30 дней:</b>\nВсего заказов: <b>{orders_count}</b>\nОбщая сумма: <b>{total_sum:.2f} ₽</b>\nТоп-товары:\n' + ('\n'.join(top_lines) if top_lines else '—')
    await callback.message.edit_text(stats_text, reply_markup=stats_actions())
    await callback.answer()

@router.callback_query(F.data == 'admin_export_orders_csv')
@admin_only
async def export_orders_csv(callback: CallbackQuery, t, **_):
    """
    Exports orders for the last 30 days to CSV.
	"""
    date_from = datetime.now() - timedelta(days=30)
    orders = await Order.filter(created_at__gte=date_from).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Дата', 'Покупатель', t('user_checkout_keyboards.buttons.telefon'), 'Сумма', 'Статус', t('user_checkout_keyboards.buttons.sposob-oplaty'), 'Доставка', t('user_checkout_keyboards.buttons.adres'), t('user_checkout_keyboards.buttons.kommentarij')])
    for o in orders:
        await o.fetch_related('user')
        writer.writerow([o.id, o.created_at.strftime('%d.%m.%Y %H:%M'), getattr(o.user, 'full_name', '-'), getattr(o.user, 'phone', '-'), f'{o.total_price:.2f}', o.status, o.payment_method, o.delivery_method, o.address, o.comment])
    output.seek(0)
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmpfile:
        tmpfile.write(output.read().encode('utf-8'))
        tmpfile_path = tmpfile.name
    file_name = f"orders_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    await callback.message.answer_document(FSInputFile(tmpfile_path, filename=file_name), caption='Экспорт заказов за 30 дней (CSV)')
    await callback.answer()
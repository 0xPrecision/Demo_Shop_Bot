from typing import Optional, List, Tuple, Any
from decimal import Decimal
from database.models import User, Product, Category, Cart, Order, OrderItem

# -------- USERS --------

async def get_or_create_user_profile(user_id: int) -> Optional[User]:
    """
    Возвращает профиль пользователя по Telegram ID.
    Если профиль ещё не создан, заполняет поля дефолтными значениями.
    :param user_id: Telegram user ID.
    :return: Объект User или None.
    """
    user = await User.get_or_none(id=user_id)
    if not user:
        user = await User.create(id=user_id, full_name="", phone="", address="")
    return user

async def update_user_profile(user_id: int, name: str = None, phone: str = None, address: str = None) -> User | None:
    """
    Обновляет профиль пользователя.
    :param user_id: Telegram user ID.
    :param name: Имя пользователя.
    :param phone: Телефон.
    :param address: Адрес (опционально).
    :return: Объект User.
    """
    user = await User.get_or_none(id=user_id)
    if not user:
        return None
    if name is not None:
        user.full_name = name
    if phone is not None:
        user.phone = phone
    if address is not None:
        user.address = address
    await user.save()
    return user

async def create_user_profile(user_id: int, name: str, phone: str, address: str) -> User:
    """
    Создаёт профиль пользователя.
    :param user_id: Telegram user ID.
    :param name: Имя пользователя.
    :param phone: Телефон.
    :param address: Адрес (опционально).
    :return: Объект User.
    """
    user = await User.get_or_none(id=user_id)
    if user is None:
        return await User.create(id=user_id, full_name=name, phone=phone, address=address)
    else:
        user.full_name = name
        user.phone = phone
        user.address = address
        await user.save()
    return user

# -------- CATEGORIES --------

async def create_category(name: str) -> Category:
    """
    Создаёт новую категорию.
    :param name: Название категории.
    :return: Объект Category.
    """
    category, _ = await Category.get_or_create(name=name)
    return category

async def get_all_categories() -> List[Category]:
    """
    Возвращает список всех категорий.
    :return: Список объектов Category.
    """
    return await Category.all()

async def update_category(cat_id: int, new_name: str):
    """ Обновляет наименование категории."""
    return await Category.filter(id=cat_id).update(name=new_name)

async def get_category_by_name(name: str):
    """
    Возвращает объект категории по её названию.
    """
    return await Category.get(name=name)

# -------- PRODUCTS --------

async def create_product(
    name: str,
    description: str,
    price: Decimal,
    stock: int,
    category: Category,
    photo: str = None,
    is_active: bool = True
) -> Product:
    """
    Создаёт новый товар.
    :param name: Название товара.
    :param description: Описание товара.
    :param price: Цена.
    :param stock: Количество на складе.
    :param category: Объект категории.
    :param photo: File ID фото.
    :param is_active: Активен ли товар.
    :return: Объект Product.
    """
    return await Product.create(
        name=name,
        description=description,
        price=price,
        stock=stock,
        category=category,
        photo=photo,
        is_active=is_active
    )

async def update_product(product_id: int, **fields: Any):
    """
    Обновляет выбранные поля товара по product_id.
    :param product_id: ID товара.
    :param fields: Ключ-значение, где ключ — поле модели Product, значение — новое значение.
    :return: Количество обновлённых строк (int)
    """
    # Если в fields есть category как объект — вытаскиваем id:
    if "category" in fields and fields["category"]:
        category = fields["category"]
        if hasattr(category, "id"):
            fields["category_id"] = category.id
        else:
            # Если пришло строкой (название), лучше получить объект категории заранее!
            raise ValueError("category должен быть объектом Category")
        del fields["category"]

    updated_count = await Product.filter(id=product_id).update(**fields)
    return updated_count

async def get_all_products() -> List[Product]:
    """
    Возвращает список всех товаров.
    :return: Список объектов Product.
    """
    return await Product.filter(is_active=True).prefetch_related("category").all()

async def get_products_by_category(category: Category) -> List[Product]:
    """
    Возвращает список товаров по категории.
    :param category: Объект категории.
    :return: Список объектов Product.
    """
    return await Product.filter(category=category, is_active=True).all()

async def get_products_page_by_category(category_id: int, page: int = 1, page_size: int = 10):
    """
    Получает товары определённой категории с пагинацией.
    :param category_id: Название категории
    :param page: Страница (от 1)
    :param page_size: Кол-во товаров на странице
    :return: (список товаров, has_next, has_prev)
    """
    total = await Product.filter(category_id=category_id, is_active=True).count()
    total_pages = (total + page_size - 1) // page_size
    skip = (page - 1) * page_size
    products = await Product.filter(category_id=category_id, is_active=True).order_by('-id').offset(skip).limit(page_size)
    has_prev = page > 1
    has_next = page < total_pages
    return products, has_next, has_prev

async def get_product_by_id(product_id: int) -> Optional[Product]:
    """
    Возвращает товар по его id.
    :param product_id: ID товара.
    :return: Объект Product или None.
    """
    return await Product.get_or_none(id=product_id)


async def get_products_page(page: int = 1, page_size: int = 10) -> Tuple[List[Product], bool, bool]:
    total = await Product.filter(is_active=True).all().count()
    total_pages = (total + page_size - 1) // page_size
    skip = (page - 1) * page_size
    products = await Product.filter(is_active=True).order_by('-id').offset(skip).limit(page_size)
    has_prev = page > 1
    has_next = page < total_pages
    return products, has_next, has_prev


# -------- CART --------

async def add_to_cart(user_id: int, product_id: int, quantity: int) -> Cart:
    """
    Добавляет товар в корзину пользователя или увеличивает количество, если уже есть.
    :param user_id: ID пользователя.
    :param product_id: ID товара.
    :param quantity: Количество.
    :return: Объект Cart (позиция в корзине).
    """
    user = await get_or_create_user_profile(user_id)
    product = await Product.get(id=product_id)
    cart_item = await Cart.get_or_none(user=user, product=product)
    if cart_item:
        cart_item.quantity += quantity
        await cart_item.save()
    else:
        cart_item = await Cart.create(user=user, product=product, quantity=quantity)
    return cart_item

async def get_cart(user_id: int) -> List[Cart]:
    """
    Возвращает корзину пользователя (список позиций Cart).
    :param user_id: ID пользователя.
    :return: Список Cart.
    """
    user = await get_or_create_user_profile(user_id)
    return await Cart.filter(user=user).prefetch_related("product").all()

async def remove_from_cart(user_id: int, product_id: int) -> None:
    """
    Удаляет позицию товара из корзины пользователя.
    :param user_id: Telegram ID пользователя.
    :param product_id: ID товара для удаления из корзины.
    :return: None
    """
    user = await get_or_create_user_profile(user_id)
    await Cart.filter(user=user, product=product_id).delete()

async def clear_cart(user_id: int) -> None:
    """
    Очищает корзину пользователя.
    :param user_id: ID пользователя.
    :return: None
    """
    user = await get_or_create_user_profile(user_id)
    await Cart.filter(user=user).delete()

# -------- ORDERS --------

async def create_order(
    user_id: int,
    name: str = "-",
    phone: str = "-",
    status: str = "🔧 В обработке",
    payment_method: str = "-",
    delivery_method: str = "-",
    address: str = "-",
    comment: str = "-",
) -> Optional[Order]:
    """
    Создаёт заказ на основе корзины пользователя.
    :param user_id: ID пользователя.
    :param name: ФИО пользователя.
    :param phone: Номер телефона пользователя.
    :param status: Статус заказа.
    :param payment_method: Способ оплаты.
    :param delivery_method: Способ доставки.
    :param address: Адрес доставки.
    :param comment: Комментарий.
    :return: Объект Order или None, если корзина пуста.
    """
    user = await get_or_create_user_profile(user_id)
    cart_items = await Cart.filter(user=user).prefetch_related('product')
    if not cart_items:
        return None
    order = await Order.create(
        user=user,
        name=name,
        phone=phone,
        status=status,
        total_price=0,
        payment_method=payment_method,
        delivery_method=delivery_method,
        address=address,
        comment=comment
    )
    total = 0
    for item in cart_items:
        await OrderItem.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price_at_order=item.product.price
        )
        total += Decimal(item.product.price) * item.quantity
    order.total_price = total
    await order.save()
    await clear_cart(user_id)
    return order

async def get_orders(user_id: int = None) -> List[Order]:
    """
    Возвращает список заказов пользователя.
    :param user_id: ID пользователя.
    :return: Список заказов (Order).
    """
    if user_id:
        return await Order.filter(user_id=user_id)
    else:
        return await Order.all().order_by('-created_at')

async def get_order_items(order: Order) -> List[OrderItem]:
    """
    Возвращает позиции определённого заказа.
    :param order: Объект заказа.
    :return: Список позиций заказа (OrderItem).
    """
    return await OrderItem.filter(order=order).prefetch_related('product').all()

async def get_order_by_id(order_id: int) -> Optional[Order]:
    """
    Возвращает заказ по его id.
    :param order_id: ID заказа.
    :return: Объект Order или None.
    """
    order = await Order.get_or_none(id=order_id)
    if order:
        await order.fetch_related('user')
    return order

async def get_orders_page(page: int = 1, page_size: int = 10) -> Tuple[List[Order], bool, bool]:
    total = await Order.all().count()
    total_pages = (total + page_size - 1) // page_size
    skip = (page - 1) * page_size
    orders = await Order.all().order_by('-created_at').offset(skip).limit(page_size)
    has_prev = page > 1
    has_next = page < total_pages
    return orders, has_next, has_prev
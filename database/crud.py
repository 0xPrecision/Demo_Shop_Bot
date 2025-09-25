from typing import Optional, List, Tuple, Any
from decimal import Decimal
from database.models import User, Product, Category, Cart, Order, OrderItem

# -------- USERS --------

async def get_or_create_user_profile(user_id: int) -> Optional[User]:
    """
    Returns the user profile by Telegram ID.
    If the profile does not exist, fills fields with default values.
    :param user_id: Telegram user ID.
    :return: User object or None.
	"""
    user = await User.get_or_none(id=user_id)
    if not user:
        user = await User.create(id=user_id, full_name="", phone="", address="")
    return user

async def update_user_profile(user_id: int, name: str = None, phone: str = None, address: str = None) -> User | None:
    """
    Updates the user profile.
    :param user_id: Telegram user ID.
    :param name: User name.
    :param phone: Phone.
    :param address: Address (optional).
    :return: User object.
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
    Creates a user profile.
    :param user_id: Telegram user ID.
    :param name: User name.
    :param phone: Phone.
    :param address: Address (optional).
    :return: User object.
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
    Creates a new category.
    :param name: Category name.
    :return: Category object.
	"""
    category, _ = await Category.get_or_create(name=name)
    return category

async def get_all_categories() -> List[Category]:
    """
    Returns the list of all categories.
    :return: List of Category objects.
	"""
    return await Category.all()

async def update_category(cat_id: int, new_name: str):
    """
    Updates the category name.
	"""
    return await Category.filter(id=cat_id).update(name=new_name)

async def get_category_by_name(name: str):
    """
    Returns a category object by its name.
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
    Creates a new product.
    :param name: Product name.
    :param description: Product description.
    :param price: Price.
    :param stock: Stock quantity.
    :param category: Category object.
    :param photo: Photo file ID.
    :param is_active: Whether the product is active.
    :return: Product object.
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
    Updates selected product fields by product_id.
    :param product_id: Product ID.
    :param fields: Key-value pairs where the key is a Product field and the value is the new value.
    :return: Number of updated rows (int)
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
    Returns the list of all products.
    :return: List of Product objects.
	"""
    return await Product.filter(is_active=True).prefetch_related("category").all()

async def get_products_by_category(category: Category) -> List[Product]:
    """
    Returns the list of products for a category.
    :param category: Category object.
    :return: List of Product objects.
	"""
    return await Product.filter(category=category, is_active=True).all()

async def get_products_page_by_category(category_id: int, page: int = 1, page_size: int = 10):
    """
    Retrieves products of a given category with pagination.
    :param category_id: Category name
    :param page: Page (from 1)
    :param page_size: Number of products per page
    :return: (list of products, has_next, has_prev)
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
    Returns a product by its ID.
    :param product_id: Product ID.
    :return: Product object or None.
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
    Adds a product to the user's cart or increases the quantity if it already exists.
    :param user_id: User ID.
    :param product_id: Product ID.
    :param quantity: Quantity.
    :return: Cart object (cart item).
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
    Returns the user's cart (list of Cart items).
    :param user_id: User ID.
    :return: List of Cart.
	"""
    user = await get_or_create_user_profile(user_id)
    return await Cart.filter(user=user).prefetch_related("product").all()

async def remove_from_cart(user_id: int, product_id: int) -> None:
    """
    Removes a product item from the user's cart.
    :param user_id: Telegram user ID.
    :param product_id: Product ID to remove from the cart.
    :return: None
	"""
    user = await get_or_create_user_profile(user_id)
    await Cart.filter(user=user, product=product_id).delete()

async def clear_cart(user_id: int) -> None:
    """
    Clears the user's cart.
    :param user_id: User ID.
    :return: None
	"""
    user = await get_or_create_user_profile(user_id)
    await Cart.filter(user=user).delete()

# -------- ORDERS --------

async def create_order(
    user_id: int,
    name: str = "-",
    phone: str = "-",
    status: str = None,
    payment_method: str = "-",
    delivery_method: str = "-",
    address: str = "-",
    comment: str = "-",
) -> Optional[Order]:
    """
    Creates an order from the user's cart.
    :param user_id: User ID.
    :param name: User full name.
    :param phone: User phone number.
    :param status: Order status.
    :param payment_method: Payment method.
    :param delivery_method: Delivery method.
    :param address: Delivery address.
    :param comment: Comment.
    :return: Order object or None if the cart is empty.
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
    Returns the list of user orders.
    :param user_id: User ID.
    :return: List of orders (Order).
	"""
    if user_id:
        return await Order.filter(user_id=user_id)
    else:
        return await Order.all().order_by('-created_at')

async def get_order_items(order: Order) -> List[OrderItem]:
    """
    Returns the items of a given order.
    :param order: Order object.
    :return: List of order items (OrderItem).
	"""
    return await OrderItem.filter(order=order).prefetch_related('product').all()

async def get_order_by_id(order_id: int) -> Optional[Order]:
    """
    Returns an order by its ID.
    :param order_id: Order ID.
    :return: Order object or None.
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
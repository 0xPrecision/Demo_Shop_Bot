from tortoise import fields
from tortoise.models import Model


class User(Model):
    """
    User model.

    :param id: Telegram user ID.
    :param username: User's username.
    :param full_name: User's full name.
    :param phone: Phone.
    :param created_at: Registration date.
    :param is_active: Whether the user is active.
    """

    id = fields.BigIntField(pk=True)
    username = fields.CharField(max_length=64, null=True)
    full_name = fields.CharField(max_length=128)
    phone = fields.CharField(max_length=20, null=True)
    address = fields.CharField(max_length=128)
    created_at = fields.DatetimeField(auto_now_add=True)
    is_active = fields.BooleanField(default=True)


class UserLocale(Model):
    """
    One-to-one to User. PK = user_id.
    """

    user: fields.OneToOneRelation[User] = fields.OneToOneField(
        "models.User", pk=True, related_name="locale_pref", on_delete=fields.RESTRICT
    )
    locale = fields.CharField(max_length=8)


class Product(Model):
    """
    Product model.

    :param id: Product ID.
    :param name: Product name.
    :param description: Product description.
    :param price: Product price.
    :param stock: Stock quantity.
    :param is_active: Active flag.
    :param created_at: Date added.
    :param category: Category (relation to Category).
    """

    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=128)
    description = fields.TextField(null=True)
    price = fields.DecimalField(max_digits=10, decimal_places=2)
    stock = fields.IntField()
    is_active = fields.BooleanField(default=True)
    photo = fields.CharField(max_length=256, null=True, default=None)
    created_at = fields.DatetimeField(auto_now_add=True)
    category = fields.ForeignKeyField(
        "models.Category", related_name="products", null=True
    )

    @property
    def status_key(self) -> str:
        return "product.status.active" if self.is_active else "product.status.archived"

    def status_label(self, t) -> str:
        return t(self.status_key)


class Category(Model):
    """
    Product category model.
    :param id: Category ID (auto).
    :param name: Category name.
    """

    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name


class Order(Model):
    """
    Order model.

    :param id: Order ID.
    :param user: User (ForeignKey to User).
    :param created_at: Order creation date.
    :param status: Order status (e.g., 'In progress', 'Completed').
    :param total_price: Total order amount.
    :param payment_method: Payment method.
    :param delivery_method: Delivery method.
    :param address: Delivery address.
    :param comment: User comment on the order.
    """

    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="orders")
    name = fields.CharField(max_length=128, null=True)
    phone = fields.CharField(max_length=20, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    status = fields.CharField(max_length=32, default="In progress")
    total_price = fields.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = fields.CharField(max_length=64, null=True)
    delivery_method = fields.CharField(max_length=64, null=True)
    address = fields.CharField(max_length=255, null=True)
    comment = fields.TextField(null=True)


class OrderItem(Model):
    """
    Order item (product within an order).

    :param id: Order item ID.
    :param order: Order (relation to Order).
    :param product: Product (relation to Product).
    :param quantity: Quantity of the product.
    :param price_at_order: Product price at the time of order.
    """

    id = fields.IntField(pk=True)
    order = fields.ForeignKeyField("models.Order", related_name="items")
    product = fields.ForeignKeyField("models.Product", related_name="order_items")
    quantity = fields.IntField()
    price_at_order = fields.DecimalField(max_digits=10, decimal_places=2)


class Cart(Model):
    """
    Cart item.

    :param id: Cart item ID.
    :param user: User (relation to User).
    :param product: Product (relation to Product).
    :param quantity: Quantity.
    """

    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="cart")
    product = fields.ForeignKeyField("models.Product", related_name="+")
    quantity = fields.IntField()

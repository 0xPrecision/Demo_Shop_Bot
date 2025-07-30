from tortoise import fields
from tortoise.models import Model

class User(Model):
    """
    Модель пользователя.

    :param id: Telegram ID пользователя.
    :param username: Username пользователя.
    :param full_name: Имя и фамилия пользователя.
    :param phone: Телефон.
    :param created_at: Дата регистрации.
    :param is_active: Активен ли пользователь.
    """
    id = fields.BigIntField(pk=True)
    username = fields.CharField(max_length=64, null=True)
    full_name = fields.CharField(max_length=128)
    phone = fields.CharField(max_length=20, null=True)
    address = fields.CharField(max_length=128)
    created_at = fields.DatetimeField(auto_now_add=True)
    is_active = fields.BooleanField(default=True)

class Product(Model):
    """
    Модель товара.

    :param id: ID товара.
    :param name: Название товара.
    :param description: Описание товара.
    :param price: Цена товара.
    :param stock: Количество на складе.
    :param is_active: Признак активности.
    :param created_at: Дата добавления.
    :param category: Категория (связь с Category).
    """
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=128)
    description = fields.TextField(null=True)
    price = fields.DecimalField(max_digits=10, decimal_places=2)
    stock = fields.IntField()
    is_active = fields.BooleanField(default=True)
    photo = fields.CharField(max_length=256, null=True, default=None)
    created_at = fields.DatetimeField(auto_now_add=True)
    category = fields.ForeignKeyField("models.Category", related_name="products", null=True)

class Category(Model):
    """
    Модель категории товара.
    :param id: ID категории (автоматически).
    :param name: Название категории.
    """
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name

class Order(Model):
    """
    Модель заказа.

    :param id: ID заказа.
    :param user: Пользователь (ForeignKey к User).
    :param created_at: Дата создания заказа.
    :param status: Статус заказа (например, 'В работе', 'Выполнен').
    :param total_price: Общая сумма заказа.
    :param payment_method: Способ оплаты.
    :param delivery_method: Способ доставки.
    :param address: Адрес доставки.
    :param comment: Комментарий пользователя к заказу.
    """
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='orders')
    name = fields.CharField(max_length=128, null=True)
    phone = fields.CharField(max_length=20, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    status = fields.CharField(max_length=32, default='В работе')
    total_price = fields.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = fields.CharField(max_length=64, null=True)
    delivery_method = fields.CharField(max_length=64, null=True)
    address = fields.CharField(max_length=255, null=True)
    comment = fields.TextField(null=True)

class OrderItem(Model):
    """
    Позиция заказа (товар в заказе).

    :param id: ID позиции заказа.
    :param order: Заказ (связь с Order).
    :param product: Товар (связь с Product).
    :param quantity: Количество товара.
    :param price_at_order: Цена товара в момент заказа.
    """
    id = fields.IntField(pk=True)
    order = fields.ForeignKeyField('models.Order', related_name='items')
    product = fields.ForeignKeyField('models.Product', related_name='order_items')
    quantity = fields.IntField()
    price_at_order = fields.DecimalField(max_digits=10, decimal_places=2)

class Cart(Model):
    """
    Позиция в корзине пользователя.

    :param id: ID позиции в корзине.
    :param user: Пользователь (связь с User).
    :param product: Товар (связь с Product).
    :param quantity: Количество.
    """
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='cart')
    product = fields.ForeignKeyField('models.Product', related_name='+')
    quantity = fields.IntField()


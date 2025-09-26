# config.py

TORTOISE_ORM = {
    "connections": {
        "default": "sqlite://shop.db",  # можно вынести в .env
    },
    "apps": {
        "models": {
            "models": [
                "database.models",  # твои модели
                "aerich.models",  # служебные таблицы Aerich
            ],
            "default_connection": "default",
        },
    },
}

import shutil
import os
from datetime import datetime

from tortoise import Tortoise


def backup_sqlite_db(db_path: str = "shop.db", backup_dir: str = "backups") -> None:
    """
    Создаёт резервную копию SQLite-базы перед запуском приложения.

    Args:
        db_path (str): Путь к файлу базы данных.
        backup_dir (str): Папка для хранения резервных копий.
    """
    if os.path.exists(db_path):
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"shop_backup_{timestamp}.db")
        shutil.copy2(db_path, backup_file)

async def init_db(db_url: str = "sqlite://shop.db") -> None:
    """
    Инициализация подключения к базе данных и создание таблиц, если они ещё не созданы.
    """
    if db_url.startswith("sqlite://"):
        db_path = db_url.replace("sqlite://", "")
    else:
        db_path = db_url

    db_exists = os.path.exists(db_path)

    # Делаем бэкап только если это SQLite и файл существует
    if db_url.startswith("sqlite://") and db_exists:
        backup_sqlite_db(db_path)

    await Tortoise.init(
        db_url=db_url,
        modules={"models": ["database.models"]}
    )
    if not db_exists:
        await Tortoise.generate_schemas()

async def close_db() -> None:
    """
    Корректное закрытие всех соединений с БД.
    """
    await Tortoise.close_connections()

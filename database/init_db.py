# import os
# import shutil
# from datetime import datetime
#
# from tortoise import Tortoise
#
#
# def backup_sqlite_db(db_path: str = "shop.db", backup_dir: str = "backups") -> None:
#     """
#     Creates a backup of the SQLite database before launching the application.
#
#     Args:
#     db_path (str): Path to the database file.
#     backup_dir (str): Directory for storing backups.
#     """
#     if os.path.exists(db_path):
#         os.makedirs(backup_dir, exist_ok=True)
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         backup_file = os.path.join(backup_dir, f"shop_backup_{timestamp}.db")
#         shutil.copy2(db_path, backup_file)
#
#
# async def init_db(db_url: str = "sqlite://shop.db") -> None:
#     """
#     Initializes the database connection and creates tables if they do not already exist.
#     """
#     if db_url.startswith("sqlite://"):
#         db_path = db_url.replace("sqlite://", "")
#     else:
#         db_path = db_url
#
#     db_exists = os.path.exists(db_path)
#
#     # Делаем бэкап только если это SQLite и файл существует
#     if db_url.startswith("sqlite://") and db_exists:
#         backup_sqlite_db(db_path)
#
#     await Tortoise.init(db_url=db_url, modules={"models": ["database.models"]})
#     if not db_exists:
#         await Tortoise.generate_schemas()
#
#
# async def close_db() -> None:
#     """
#     Properly closes all database connections.
#     """
#     await Tortoise.close_connections()


# database/init_db.py
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from aerich import Command
from tortoise import Tortoise

try:
    from database.config import TORTOISE_ORM
except Exception as e:
    raise RuntimeError(
        "config.TORTOISE_ORM not found. Create config.py with Tortoise settings."
    ) from e


def _sqlite_file_from_url(db_url: str) -> Optional[Path]:
    """
    Extract the SQLite file path from a sqlite:// URL.
    Supports both relative ('sqlite://shop.db') and absolute ('sqlite:///abs/path/shop.db') paths.
    """
    if not db_url.startswith("sqlite://"):
        return None
    rest = db_url[len("sqlite://") :]
    return Path(rest)


def backup_sqlite_db(db_url: str) -> None:
    """
    Create a backup of the SQLite database before running migrations.

    Args:
        db_url (str): Database URL (must be SQLite).
    """
    db_path = _sqlite_file_from_url(db_url)
    if not db_path:
        return
    if db_path.exists():
        backup_dir = Path("backups")
        backup_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copy2(db_path, backup_dir / f"shop_backup_{ts}.db")


async def init_db() -> None:
    """
    Initialize the database properly:
    1. Backup SQLite file if it exists.
    2. If migrations exist — run `aerich upgrade`.
    3. If no migrations and database does not exist — run `generate_schemas()` once.
    4. If database exists but no migrations — just connect and continue.
    """
    db_url = TORTOISE_ORM["connections"]["default"]
    db_path = _sqlite_file_from_url(db_url)
    db_exists = bool(db_path and db_path.exists())

    if db_exists:
        backup_sqlite_db(db_url)

    migrations_root = Path("migrations")

    if migrations_root.exists() and any(migrations_root.glob("**/*.json")):
        cmd = Command(
            tortoise_config=TORTOISE_ORM, app="models", location=str(migrations_root)
        )
        await cmd.init()
        await cmd.upgrade()
    else:
        if not db_exists:
            await Tortoise.init(config=TORTOISE_ORM)
            await Tortoise.generate_schemas()
        else:
            await Tortoise.init(config=TORTOISE_ORM)


async def close_db() -> None:
    """
    Close all database connections cleanly.
    """
    await Tortoise.close_connections()

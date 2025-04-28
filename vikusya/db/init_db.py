# vikusya/db/init_db.py
from vikusya.db.connection import engine
from vikusya.db.models import Base
from vikusya.utils.logger import log_action

def init_database():
    """
    Инициализирует структуру БД (создаёт таблицы, если их нет).
    """
    Base.metadata.create_all(bind=engine)
    log_action("Инициализация БД завершена: таблицы созданы или уже существуют", category="database")

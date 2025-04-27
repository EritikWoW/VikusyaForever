import psycopg2
import os
from dotenv import load_dotenv
from vikusya.utils.logger import log_action, log_error

load_dotenv()

DB_NAME = os.environ["POSTGRES_DB"]
DB_USER = os.environ["POSTGRES_USER"]
DB_PASSWORD = os.environ["POSTGRES_PASSWORD"]
DB_HOST = os.environ["POSTGRES_HOST"]
DB_PORT = os.environ["POSTGRES_PORT"]

def ensure_database_exists():
    """
    Проверяет наличие базы данных и создаёт её, если отсутствует.
    Логирует только в случае реального создания базы.
    """
    try:
        conn = psycopg2.connect(
            dbname="postgres",  # Подключаемся к системной БД!
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.autocommit = True
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
        exists = cursor.fetchone()

        if not exists:
            cursor.execute(f"CREATE DATABASE {DB_NAME}")
            log_action(f"Создала базу данных '{DB_NAME}' 🥰", category="database")
        # Если база уже есть — ничего не пишем в лог.

        cursor.close()
        conn.close()

    except Exception as e:
        log_error(f"Ошибка при проверке/создании базы данных: {e}", category="database")

def get_connection():
    """
    Возвращает подключение к нужной базе данных.
    """
    try:
        return psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
    except Exception as e:
        log_error(f"Не удалось подключиться к базе данных '{DB_NAME}': {e}", category="database")
        raise

import os
import psycopg2
from dotenv import load_dotenv
from vikusya.utils.logger import log_error

load_dotenv()

DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

def get_connection():
    """
    Получает новое подключение к базе данных.
    Использует переменные окружения из .env.
    """
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        return conn
    except Exception as e:
        log_error(f"Не удалось подключиться к базе данных: {e}", category="database")
        raise e
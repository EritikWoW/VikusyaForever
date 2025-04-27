import psycopg2
import os
from dotenv import load_dotenv
from vikusya.utils.logger import log_action, log_error

load_dotenv()

DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")

def ensure_database_exists():
    try:
        conn = psycopg2.connect(
            dbname="postgres",  # подключаемся к системной БД
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.autocommit = True
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (DB_NAME,))
        exists = cursor.fetchone()

        if not exists:
            cursor.execute(f"CREATE DATABASE {DB_NAME};")
            log_action(f"Создала базу данных '{DB_NAME}'", category="database")
        else:
            log_action(f"База данных '{DB_NAME}' уже существует", category="database")

        cursor.close()
        conn.close()

    except Exception as e:
        log_error(f"Ошибка при проверке/создании БД: {e}", category="database")

from vikusya.db.connection import get_connection
from vikusya.utils.logger import log_action, log_error

def insert_lexeme(word, part_of_speech=None, gender=None, animate=None, description=None):
    """Добавляет новое слово (лексему) в базу, если его ещё нет."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO Lexemes (Word, PartOfSpeech, Gender, Animate, Description)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (Word) DO NOTHING
            RETURNING Id;
            """,
            (word, part_of_speech, gender, animate, description)
        )
        row = cursor.fetchone()
        if row:
            log_action(f"Добавила лексему: '{word}' (часть речи: {part_of_speech})", category="lexemes")
        else:
            cursor.execute("SELECT Id FROM Lexemes WHERE Word = %s;", (word,))
            row = cursor.fetchone()
        return row[0]
    except Exception as e:
        log_error(f"Ошибка при добавлении лексемы '{word}': {e}", category="lexemes")
        return None
    finally:
        conn.commit()
        cursor.close()
        conn.close()

def get_lexeme_id(word):
    """Возвращает ID лексемы по слову."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT Id FROM Lexemes WHERE Word = %s;", (word,))
        row = cursor.fetchone()
        return row[0] if row else None
    except Exception as e:
        log_error(f"Ошибка при поиске лексемы '{word}': {e}", category="lexemes")
        return None
    finally:
        cursor.close()
        conn.close()

def get_all_lexemes():
    """Возвращает все лексемы."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT Id, Word, PartOfSpeech, Gender, Animate, Description FROM Lexemes ORDER BY Word;")
        return cursor.fetchall()
    except Exception as e:
        log_error(f"Ошибка при получении списка лексем: {e}", category="lexemes")
        return []
    finally:
        cursor.close()
        conn.close()

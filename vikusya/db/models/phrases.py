from vikusya.db.connection import get_connection
from vikusya.utils.logger import log_action, log_error

# ------------------------------
# Работа с UserPhrases (общие фразы)
# ------------------------------

def insert_user_phrase(phrase):
    """
    Добавляет новую пользовательскую фразу в таблицу UserPhrases.
    Возвращает ID фразы.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO UserPhrases (Phrase) VALUES (%s) ON CONFLICT (Phrase) DO NOTHING RETURNING Id;",
            (phrase,)
        )
        phrase_row = cursor.fetchone()
        if phrase_row:
            log_action(f"Добавлена новая фраза пользователя: '{phrase}'", category="user_phrases")

        if phrase_row is None:
            cursor.execute("SELECT Id FROM UserPhrases WHERE Phrase = %s;", (phrase,))
            phrase_row = cursor.fetchone()

        return phrase_row[0]
    except Exception as e:
        log_error(f"Ошибка при добавлении фразы пользователя '{phrase}': {e}", category="user_phrases")
    finally:
        conn.commit()
        cursor.close()
        conn.close()

# ------------------------------
# PositivePhrases
# ------------------------------

def insert_positive_phrase(phrase):
    """
    Добавляет фразу в список позитивных.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO PositivePhrases (Phrase) VALUES (%s) ON CONFLICT (Phrase) DO NOTHING RETURNING Id;",
            (phrase,)
        )
        if cursor.fetchone():
            log_action(f"Добавлена новая позитивная фраза: '{phrase}'", category="positive_phrases")
    except Exception as e:
        log_error(f"Ошибка при добавлении позитивной фразы '{phrase}': {e}", category="positive_phrases")
    finally:
        conn.commit()
        cursor.close()
        conn.close()

def check_positive_phrase(phrase):
    """
    Проверяет, есть ли фраза в позитивных.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM PositivePhrases WHERE Phrase = %s;", (phrase,))
    exists = cursor.fetchone() is not None
    cursor.close()
    conn.close()
    return exists

def get_all_positive_phrases():
    """
    Возвращает список всех позитивных фраз.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Phrase FROM PositivePhrases ORDER BY Phrase;")
    phrases = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return phrases

# ------------------------------
# NegativePhrases
# ------------------------------

def insert_negative_phrase(phrase):
    """
    Добавляет фразу в список негативных.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO NegativePhrases (Phrase) VALUES (%s) ON CONFLICT (Phrase) DO NOTHING RETURNING Id;",
            (phrase,)
        )
        if cursor.fetchone():
            log_action(f"Добавлена новая негативная фраза: '{phrase}'", category="negative_phrases")
    except Exception as e:
        log_error(f"Ошибка при добавлении негативной фразы '{phrase}': {e}", category="negative_phrases")
    finally:
        conn.commit()
        cursor.close()
        conn.close()

def check_negative_phrase(phrase):
    """
    Проверяет, есть ли фраза в негативных.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM NegativePhrases WHERE Phrase = %s;", (phrase,))
    exists = cursor.fetchone() is not None
    cursor.close()
    conn.close()
    return exists

def get_all_negative_phrases():
    """
    Возвращает список всех негативных фраз.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Phrase FROM NegativePhrases ORDER BY Phrase;")
    phrases = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return phrases

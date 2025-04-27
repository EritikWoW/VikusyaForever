from vikusya.db.connection import get_connection
from vikusya.utils.logger import log_action, log_error

def insert_user_phrase(phrase):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO UserPhrases (Phrase) VALUES (%s) ON CONFLICT (Phrase) DO NOTHING RETURNING Id;",
        (phrase,)
    )
    phrase_row = cursor.fetchone()
    if phrase_row:
        log_action(f"Добавила новую фразу пользователя: '{phrase}'", category="phrases")

    if phrase_row is None:
        cursor.execute("SELECT Id FROM UserPhrases WHERE Phrase = %s;", (phrase,))
        phrase_row = cursor.fetchone()

    conn.commit()
    cursor.close()
    conn.close()
    return phrase_row[0]

def insert_positive_phrase(phrase):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO PositivePhrases (Phrase) VALUES (%s) ON CONFLICT (Phrase) DO NOTHING RETURNING Id;",
            (phrase,)
        )
        if cursor.fetchone():
            log_action(f"Добавила новую позитивную фразу: '{phrase}'", category="phrases_positive")
    except Exception as e:
        log_error(f"Ошибка при добавлении позитивной фразы '{phrase}': {e}", category="phrases_positive")
    conn.commit()
    cursor.close()
    conn.close()

def insert_negative_phrase(phrase):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO NegativePhrases (Phrase) VALUES (%s) ON CONFLICT (Phrase) DO NOTHING RETURNING Id;",
            (phrase,)
        )
        if cursor.fetchone():
            log_action(f"Добавила новую негативную фразу: '{phrase}'", category="phrases_negative")
    except Exception as e:
        log_error(f"Ошибка при добавлении негативной фразы '{phrase}': {e}", category="phrases_negative")
    conn.commit()
    cursor.close()
    conn.close()

def check_positive_phrase(phrase):
    """Проверяет, есть ли фраза в позитивных."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM PositivePhrases WHERE Phrase = %s;",
        (phrase,)
    )
    exists = cursor.fetchone() is not None
    cursor.close()
    conn.close()
    return exists

def check_negative_phrase(phrase):
    """Проверяет, есть ли фраза в негативных."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM NegativePhrases WHERE Phrase = %s;",
        (phrase,)
    )
    exists = cursor.fetchone() is not None
    cursor.close()
    conn.close()
    return exists

def get_all_positive_phrases():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Phrase FROM PositivePhrases ORDER BY Phrase;")
    phrases = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return phrases

def get_all_negative_phrases():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Phrase FROM NegativePhrases ORDER BY Phrase;")
    phrases = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return phrases
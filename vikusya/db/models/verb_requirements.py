from vikusya.db.connection import get_connection
from vikusya.utils.logger import log_action, log_error

def insert_verb_requirement(verb, requires_preposition=False, preposition=None, required_case=None):
    """Добавляет правило управления для глагола (падеж, предлог)."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO VerbRequirements (Verb, RequiresPreposition, Preposition, RequiredCase)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (Verb) DO NOTHING
            RETURNING Id;
            """,
            (verb, requires_preposition, preposition, required_case)
        )
        row = cursor.fetchone()
        if row:
            log_action(f"Добавила правило для глагола '{verb}' (предлог: '{preposition}', падеж: '{required_case}')", category="verbs")
        else:
            cursor.execute("SELECT Id FROM VerbRequirements WHERE Verb = %s;", (verb,))
            row = cursor.fetchone()
        return row[0]
    except Exception as e:
        log_error(f"Ошибка при добавлении правила для глагола '{verb}': {e}", category="verbs")
        return None
    finally:
        conn.commit()
        cursor.close()
        conn.close()

def get_verb_requirement(verb):
    """Получает правило управления для глагола."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT Id, RequiresPreposition, Preposition, RequiredCase FROM VerbRequirements WHERE Verb = %s;",
            (verb,)
        )
        return cursor.fetchone()
    except Exception as e:
        log_error(f"Ошибка при получении правила для глагола '{verb}': {e}", category="verbs")
        return None
    finally:
        cursor.close()
        conn.close()

def get_all_verb_requirements():
    """Получает список всех правил управления глаголов."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT Id, Verb, RequiresPreposition, Preposition, RequiredCase FROM VerbRequirements ORDER BY Verb;")
        return cursor.fetchall()
    except Exception as e:
        log_error(f"Ошибка при получении списка правил управления глаголов: {e}", category="verbs")
        return []
    finally:
        cursor.close()
        conn.close()

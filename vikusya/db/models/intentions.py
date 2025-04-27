from vikusya.db.connection import get_connection
from vikusya.utils.logger import log_action, log_error

def insert_intention(subject_id, verb_id, object_id, modifier=None):
    """Добавляет намерение (subject + verb + object + modifiers)."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO Intentions (SubjectId, VerbId, ObjectId, Modifier)
            VALUES (%s, %s, %s, %s)
            RETURNING Id;
            """,
            (subject_id, verb_id, object_id, modifier)
        )
        intention_id = cursor.fetchone()[0]
        log_action(f"Добавила намерение: SubjectId={subject_id}, VerbId={verb_id}, ObjectId={object_id}, Modifier='{modifier}'", category="intentions")
        return intention_id
    except Exception as e:
        log_error(f"Ошибка при добавлении намерения (SubjectId={subject_id}, VerbId={verb_id}, ObjectId={object_id}): {e}", category="intentions")
        return None
    finally:
        conn.commit()
        cursor.close()
        conn.close()

def get_intention(intention_id):
    """Получает намерение по ID."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT Id, SubjectId, VerbId, ObjectId, Modifier, CreatedAt
            FROM Intentions
            WHERE Id = %s;
            """,
            (intention_id,)
        )
        return cursor.fetchone()
    except Exception as e:
        log_error(f"Ошибка при получении намерения с ID {intention_id}: {e}", category="intentions")
        return None
    finally:
        cursor.close()
        conn.close()

def fetch_all_intentions():
    """Получает все намерения из базы."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT Id, SubjectId, VerbId, ObjectId, Modifier, CreatedAt
            FROM Intentions
            ORDER BY CreatedAt DESC;
            """
        )
        return cursor.fetchall()
    except Exception as e:
        log_error(f"Ошибка при получении списка намерений: {e}", category="intentions")
        return []
    finally:
        cursor.close()
        conn.close()

from vikusya.db.connection import get_connection
from vikusya.utils.logger import log_action, log_error

def insert_interaction(user_input, vikusya_answer, tags=None, rating=None, notes=None):
    """Сохраняет взаимодействие (диалог) в базу данных."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO Interactions (UserInput, VikusyaAnswer, Tags, Rating, Notes)
            VALUES (%s, %s, %s, %s, %s);
            """,
            (user_input, vikusya_answer, tags, rating, notes)
        )
        log_action(f"Записала взаимодействие: '{user_input}' → '{vikusya_answer}'", category="interactions")
    except Exception as e:
        log_error(f"Ошибка при записи взаимодействия: {e}", category="interactions")
    finally:
        conn.commit()
        cursor.close()
        conn.close()

def fetch_interactions(limit=10, tag_filter=None, date_from=None, date_to=None):
    """Читает записи взаимодействий с возможностью фильтрации по тегам и датам."""
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT Id, Timestamp, UserInput, VikusyaAnswer, Tags, Rating, Notes
        FROM Interactions
        WHERE 1=1
    """
    params = []

    if tag_filter:
        query += " AND Tags ILIKE %s"
        params.append(f"%{tag_filter}%")
    if date_from:
        query += " AND Timestamp >= %s"
        params.append(date_from)
    if date_to:
        query += " AND Timestamp <= %s"
        params.append(date_to)

    query += " ORDER BY Timestamp DESC LIMIT %s"
    params.append(limit)

    try:
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        log_error(f"Ошибка при чтении взаимодействий: {e}", category="interactions")
        return []
    finally:
        cursor.close()
        conn.close()

def delete_old_interactions(days=90):
    """Удаляет взаимодействия старше N дней (по умолчанию 90)."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            DELETE FROM Interactions
            WHERE Timestamp < NOW() - INTERVAL '%s days';
            """,
            (days,)
        )
        deleted = cursor.rowcount
        log_action(f"Удалено {deleted} старых взаимодействий (старше {days} дней)", category="interactions")
    except Exception as e:
        log_error(f"Ошибка при удалении старых взаимодействий: {e}", category="interactions")
    finally:
        conn.commit()
        cursor.close()
        conn.close()

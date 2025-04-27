from vikusya.db.connection import get_connection
from vikusya.utils.logger import log_action, log_error

def insert_emotion(name, description=None):
    """
    Добавляет эмоцию, если её ещё нет.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Emotions (Name, Description) VALUES (%s, %s) ON CONFLICT (Name) DO NOTHING RETURNING Id;",
            (name, description)
        )
        emotion_row = cursor.fetchone()
        if emotion_row:
            log_action(f"Добавила новую эмоцию: '{name}'", category="emotions")

        if emotion_row is None:
            cursor.execute("SELECT Id FROM Emotions WHERE Name = %s;", (name,))
            emotion_row = cursor.fetchone()

        return emotion_row[0] if emotion_row else None

    except Exception as e:
        log_error(f"Ошибка при добавлении эмоции '{name}': {e}", category="emotions")
        return None
    finally:
        conn.commit()
        cursor.close()
        conn.close()

def get_emotion_id(name):
    """
    Получает ID эмоции по её названию.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT Id FROM Emotions WHERE Name = %s;", (name,))
        result = cursor.fetchone()
        return result[0] if result else None
    finally:
        cursor.close()
        conn.close()

def get_all_emotions():
    """
    Возвращает список всех эмоций.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT Id, Name, Description FROM Emotions ORDER BY Name;")
        emotions = cursor.fetchall()
        return emotions
    finally:
        cursor.close()
        conn.close()

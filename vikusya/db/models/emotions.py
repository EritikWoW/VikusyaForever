from vikusya.db.connection import get_connection
from vikusya.utils.logger import log_action

def insert_emotion(name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Emotions (Name) VALUES (%s) ON CONFLICT (Name) DO NOTHING RETURNING Id;",
        (name,)
    )
    emotion_row = cursor.fetchone()
    if emotion_row:
        log_action(f"Добавила новую эмоцию: '{name}'", category="emotions")

    if emotion_row is None:
        cursor.execute("SELECT Id FROM Emotions WHERE Name = %s;", (name,))
        emotion_row = cursor.fetchone()

    conn.commit()
    cursor.close()
    conn.close()
    return emotion_row[0]

def link_phrase_emotion(phrase_id, emotion_id, weight):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO PhraseEmotions (PhraseId, EmotionId, Weight)
        VALUES (%s, %s, %s)
        ON CONFLICT (PhraseId, EmotionId) DO UPDATE SET Weight = EXCLUDED.Weight;
        """,
        (phrase_id, emotion_id, weight)
    )
    log_action(f"Связала фразу ID {phrase_id} с эмоцией ID {emotion_id} (вес {weight})", category="emotions")
    conn.commit()
    cursor.close()
    conn.close()

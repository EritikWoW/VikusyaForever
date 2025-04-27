from vikusya.db.connection import get_connection
from vikusya.utils.logger import log_action, log_error

def link_lexeme_emotion_weight(lexeme_id, emotion_id, weight):
    """
    Связывает лексему с эмоцией и устанавливает вес этой связи.
    Если такая связь уже есть — обновляет вес.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO LexemeEmotionWeights (LexemeId, EmotionId, Weight)
            VALUES (%s, %s, %s)
            ON CONFLICT (LexemeId, EmotionId) DO UPDATE
            SET Weight = EXCLUDED.Weight;
            """,
            (lexeme_id, emotion_id, weight)
        )
        log_action(f"Связала лексему ID {lexeme_id} с эмоцией ID {emotion_id} (вес {weight})", category="lexeme_emotion_weights")
    except Exception as e:
        log_error(f"Ошибка при связывании лексемы ID {lexeme_id} с эмоцией ID {emotion_id}: {e}", category="lexeme_emotion_weights")
    finally:
        conn.commit()
        cursor.close()
        conn.close()

def get_emotion_weights_for_lexeme(lexeme_id):
    """
    Получает все веса эмоций для указанной лексемы.
    Возвращает список кортежей: (EmotionId, Weight)
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT EmotionId, Weight
            FROM LexemeEmotionWeights
            WHERE LexemeId = %s;
            """,
            (lexeme_id,)
        )
        weights = cursor.fetchall()
        return weights
    except Exception as e:
        log_error(f"Ошибка при получении эмоций для лексемы ID {lexeme_id}: {e}", category="lexeme_emotion_weights")
        return []
    finally:
        cursor.close()
        conn.close()

def delete_lexeme_emotion_weights(lexeme_id):
    """
    Удаляет все связи между указанной лексемой и эмоциями.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            DELETE FROM LexemeEmotionWeights
            WHERE LexemeId = %s;
            """,
            (lexeme_id,)
        )
        deleted = cursor.rowcount
        log_action(f"Удалено {deleted} связей лексемы ID {lexeme_id} с эмоциями", category="lexeme_emotion_weights")
    except Exception as e:
        log_error(f"Ошибка при удалении связей лексемы ID {lexeme_id} с эмоциями: {e}", category="lexeme_emotion_weights")
    finally:
        conn.commit()
        cursor.close()
        conn.close()

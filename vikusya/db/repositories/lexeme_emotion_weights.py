from sqlalchemy.exc import SQLAlchemyError
from vikusya.db.connection import SessionLocal
from vikusya.db.models import LexemeEmotionWeight
from vikusya.utils.logger import log_action, log_error

def link_lexeme_emotion_weight(lexeme_id, emotion_id, weight):
    """
    Получает или создаёт связь лексемы и эмоции с установкой веса.
    """
    session = SessionLocal()
    try:
        link = session.query(LexemeEmotionWeight).filter_by(
            LexemeId=lexeme_id,
            EmotionId=emotion_id
        ).first()

        if link:
            link.Weight = weight
            log_action(f"Обновила вес связи лексема {lexeme_id} ↔ эмоция {emotion_id} → {weight}", category="lexeme_emotion_weights")
        else:
            new_link = LexemeEmotionWeight(
                LexemeId=lexeme_id,
                EmotionId=emotion_id,
                Weight=weight
            )
            session.add(new_link)
            log_action(f"Создала новую связь лексема {lexeme_id} ↔ эмоция {emotion_id} с весом {weight}", category="lexeme_emotion_weights")

        session.commit()

    except SQLAlchemyError as e:
        session.rollback()
        log_error(f"Ошибка при связывании лексемы {lexeme_id} с эмоцией {emotion_id}: {e}", category="lexeme_emotion_weights")
    finally:
        session.close()

def get_emotion_weights_for_lexeme(lexeme_id):
    """
    Получает все веса эмоций для указанной лексемы.
    Возвращает список кортежей: (EmotionId, Weight)
    """
    session = SessionLocal()
    try:
        return session.query(
            LexemeEmotionWeight.EmotionId,
            LexemeEmotionWeight.Weight
        ).filter_by(LexemeId=lexeme_id).all()
    except SQLAlchemyError as e:
        log_error(f"Ошибка при получении весов эмоций для лексемы {lexeme_id}: {e}", category="lexeme_emotion_weights")
        return []
    finally:
        session.close()

def delete_lexeme_emotion_weights(lexeme_id):
    """
    Удаляет все связи между указанной лексемой и эмоциями.
    """
    session = SessionLocal()
    try:
        deleted_count = session.query(LexemeEmotionWeight).filter_by(LexemeId=lexeme_id).delete()
        session.commit()
        log_action(f"Удалено {deleted_count} связей лексемы ID {lexeme_id} с эмоциями", category="lexeme_emotion_weights")
    except SQLAlchemyError as e:
        session.rollback()
        log_error(f"Ошибка при удалении связей лексемы {lexeme_id} с эмоциями: {e}", category="lexeme_emotion_weights")
    finally:
        session.close()

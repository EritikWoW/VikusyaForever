from sqlalchemy.exc import SQLAlchemyError
from vikusya.db.connection import SessionLocal
from vikusya.db.models import Emotion
from vikusya.utils.logger import log_action, log_error

def get_or_create_emotion(name, description=None):
    """
    Получает ID эмоции, если существует, иначе добавляет новую и возвращает её ID.
    """
    session = SessionLocal()
    try:
        # Проверяем, существует ли уже такая эмоция
        emotion = session.query(Emotion).filter_by(Name=name).first()
        if emotion:
            return emotion.Id

        # Если не существует — создаём новую
        new_emotion = Emotion(Name=name, Description=description)
        session.add(new_emotion)
        session.commit()
        session.refresh(new_emotion)  # Получаем Id после вставки

        log_action(f"Добавила новую эмоцию: '{name}'", category="emotions")
        return new_emotion.Id

    except SQLAlchemyError as e:
        session.rollback()
        log_error(f"Ошибка в get_or_create_emotion для '{name}': {e}", category="emotions")
        return None
    finally:
        session.close()

def get_all_emotions():
    """
    Возвращает список всех эмоций.
    """
    session = SessionLocal()
    try:
        emotions = session.query(Emotion).order_by(Emotion.Name).all()
        return [(e.Id, e.Name, e.Description) for e in emotions]
    except SQLAlchemyError as e:
        log_error(f"Ошибка при получении списка эмоций: {e}", category="emotions")
        return []
    finally:
        session.close()

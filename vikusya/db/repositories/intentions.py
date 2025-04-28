from sqlalchemy.exc import SQLAlchemyError
from vikusya.db.connection import SessionLocal
from vikusya.db.models import Intention
from vikusya.utils.logger import log_action, log_error

def get_or_create_intention(subject_id, verb_id, object_id, modifier=None):
    """
    Получает ID намерения, если существует, иначе добавляет новое и возвращает его ID.
    """
    session = SessionLocal()
    try:
        # Проверяем, существует ли уже такое намерение
        intention = session.query(Intention).filter_by(
            SubjectId=subject_id,
            VerbId=verb_id,
            ObjectId=object_id,
            Modifier=modifier
        ).first()
        if intention:
            return intention.Id

        # Если не существует — создаём новое
        new_intention = Intention(
            SubjectId=subject_id,
            VerbId=verb_id,
            ObjectId=object_id,
            Modifier=modifier
        )
        session.add(new_intention)
        session.commit()
        session.refresh(new_intention)

        log_action(
            f"Добавила новое намерение: SubjectId={subject_id}, VerbId={verb_id}, ObjectId={object_id}, Modifier='{modifier}'",
            category="intentions"
        )
        return new_intention.Id

    except SQLAlchemyError as e:
        session.rollback()
        log_error(f"Ошибка в get_or_create_intention (SubjectId={subject_id}, VerbId={verb_id}, ObjectId={object_id}): {e}",
                  category="intentions")
        return None
    finally:
        session.close()

def get_intention(intention_id):
    """
    Получает намерение по ID.
    """
    session = SessionLocal()
    try:
        return session.query(Intention).filter(Intention.Id == intention_id).first()
    except SQLAlchemyError as e:
        log_error(f"Ошибка при получении намерения с ID {intention_id}: {e}", category="intentions")
        return None
    finally:
        session.close()

def fetch_all_intentions():
    """
    Получает все намерения из базы.
    """
    session = SessionLocal()
    try:
        return session.query(Intention).order_by(Intention.CreatedAt.desc()).all()
    except SQLAlchemyError as e:
        log_error(f"Ошибка при получении списка намерений: {e}", category="intentions")
        return []
    finally:
        session.close()

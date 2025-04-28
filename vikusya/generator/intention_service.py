# vikusya/generator/intention_service.py

from sqlalchemy.exc import SQLAlchemyError
from vikusya.db.connection import SessionLocal
from vikusya.db.models import Intention
from vikusya.utils.logger import log_action, log_error

def create_intention(subject_id, verb_id, object_id, modifier=None):
    """Создаёт новое намерение (subject + verb + object + modifier)."""
    session = SessionLocal()
    try:
        intention = Intention(
            SubjectId=subject_id,
            VerbId=verb_id,
            ObjectId=object_id,
            Modifier=modifier
        )
        session.add(intention)
        session.commit()
        session.refresh(intention)
        log_action(f"Создала намерение: SubjectId={subject_id}, VerbId={verb_id}, ObjectId={object_id}, Modifier='{modifier}'", category="intentions")
        return intention.Id
    except SQLAlchemyError as e:
        session.rollback()
        log_error(f"Ошибка при создании намерения: {e}", category="intentions")
        return None
    finally:
        session.close()

def get_intention_by_id(intention_id):
    """Получает намерение по его ID."""
    session = SessionLocal()
    try:
        return session.query(Intention).filter(Intention.Id == intention_id).first()
    except SQLAlchemyError as e:
        log_error(f"Ошибка при получении намерения с ID {intention_id}: {e}", category="intentions")
        return None
    finally:
        session.close()

def get_all_intentions():
    """Получает все намерения."""
    session = SessionLocal()
    try:
        return session.query(Intention).order_by(Intention.CreatedAt.desc()).all()
    except SQLAlchemyError as e:
        log_error(f"Ошибка при получении списка намерений: {e}", category="intentions")
        return []
    finally:
        session.close()

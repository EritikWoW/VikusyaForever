from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta

from vikusya.db.connection import SessionLocal
from vikusya.db.models import Interaction
from vikusya.utils.logger import log_action, log_error

def insert_interaction(user_input, vikusya_answer, tags=None, rating=None, notes=None):
    """
    Сохраняет взаимодействие (диалог) в базу данных.
    """
    session = SessionLocal()
    try:
        interaction = Interaction(
            UserInput=user_input,
            VikusyaAnswer=vikusya_answer,
            Tags=tags,
            Rating=rating,
            Notes=notes
        )
        session.add(interaction)
        session.commit()
        log_action(f"Записала взаимодействие: '{user_input}' → '{vikusya_answer}'", category="interactions")
    except SQLAlchemyError as e:
        session.rollback()
        log_error(f"Ошибка при записи взаимодействия: {e}", category="interactions")
    finally:
        session.close()

def fetch_interactions(limit=10, tag_filter=None, date_from=None, date_to=None):
    """
    Получает список взаимодействий с фильтрацией по тегам и датам.
    """
    session = SessionLocal()
    try:
        query = session.query(Interaction)

        if tag_filter:
            query = query.filter(Interaction.Tags.ilike(f"%{tag_filter}%"))
        if date_from:
            query = query.filter(Interaction.Timestamp >= date_from)
        if date_to:
            query = query.filter(Interaction.Timestamp <= date_to)

        return query.order_by(Interaction.Timestamp.desc()).limit(limit).all()
    except SQLAlchemyError as e:
        log_error(f"Ошибка при получении взаимодействий: {e}", category="interactions")
        return []
    finally:
        session.close()

def delete_old_interactions(days=90):
    """
    Удаляет взаимодействия старше N дней (по умолчанию 90).
    """
    session = SessionLocal()
    try:
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_count = session.query(Interaction).filter(Interaction.Timestamp < cutoff_date).delete(synchronize_session=False)
        session.commit()
        log_action(f"Удалено {deleted_count} взаимодействий старше {days} дней", category="interactions")
    except SQLAlchemyError as e:
        session.rollback()
        log_error(f"Ошибка при удалении старых взаимодействий: {e}", category="interactions")
    finally:
        session.close()

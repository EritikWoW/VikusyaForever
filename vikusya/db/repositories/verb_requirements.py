from sqlalchemy.exc import SQLAlchemyError
from vikusya.db.connection import SessionLocal
from vikusya.db.models import VerbRequirement
from vikusya.utils.logger import log_action, log_error

def get_or_create_verb_requirement(verb, requires_preposition=False, preposition=None, required_case=None):
    """
    Получает ID правила управления для глагола, если есть.
    Если нет — добавляет новое правило.
    """
    session = SessionLocal()
    try:
        existing = session.query(VerbRequirement).filter_by(Verb=verb).first()
        if existing:
            return existing.Id

        new_rule = VerbRequirement(
            Verb=verb,
            RequiresPreposition=requires_preposition,
            Preposition=preposition,
            RequiredCase=required_case
        )
        session.add(new_rule)
        session.commit()
        log_action(
            f"Добавила правило для глагола '{verb}' (предлог: '{preposition}', падеж: '{required_case}')",
            category="verbs"
        )
        return new_rule.Id
    except SQLAlchemyError as e:
        session.rollback()
        log_error(f"Ошибка при добавлении правила для глагола '{verb}': {e}", category="verbs")
        return None
    finally:
        session.close()

def get_verb_requirement(verb):
    """Получает правило управления для глагола."""
    session = SessionLocal()
    try:
        return session.query(VerbRequirement).filter_by(Verb=verb).first()
    except SQLAlchemyError as e:
        log_error(f"Ошибка при получении правила для глагола '{verb}': {e}", category="verbs")
        return None
    finally:
        session.close()

def get_all_verb_requirements():
    """Получает список всех правил управления глаголов."""
    session = SessionLocal()
    try:
        return session.query(VerbRequirement).order_by(VerbRequirement.Verb).all()
    except SQLAlchemyError as e:
        log_error(f"Ошибка при получении списка правил управления глаголов: {e}", category="verbs")
        return []
    finally:
        session.close()

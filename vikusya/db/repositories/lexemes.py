from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select
from vikusya.db.connection import SessionLocal
from vikusya.db.models import Lexeme
from vikusya.utils.logger import log_action, log_error

def get_or_create_lexeme(word, part_of_speech=None, gender=None, animate=None, description=None):
    """
    Получает ID лексемы, если существует, иначе добавляет новую и возвращает её ID.
    """
    session = SessionLocal()
    try:
        # Проверяем, существует ли уже такая лексема
        lexeme = session.query(Lexeme).filter_by(Word=word).first()
        if lexeme:
            return lexeme.Id

        # Если не существует — создаём новую
        new_lexeme = Lexeme(
            Word=word,
            PartOfSpeech=part_of_speech,
            Gender=gender,
            Animate=animate,
            Description=description
        )
        session.add(new_lexeme)
        session.commit()

        log_action(f"Добавила новую лексему (get_or_create): '{word}' (часть речи: {part_of_speech})", category="lexemes")
        return new_lexeme.Id

    except SQLAlchemyError as e:
        session.rollback()
        log_error(f"Ошибка в get_or_create_lexeme для '{word}': {e}", category="lexemes")
        return None
    finally:
        session.close()

def get_all_lexemes():
    """Возвращает все лексемы."""
    session = SessionLocal()
    try:
        lexemes = session.query(
            Lexeme.Id,
            Lexeme.Word,
            Lexeme.PartOfSpeech,
            Lexeme.Gender,
            Lexeme.Animate,
            Lexeme.Description
        ).order_by(Lexeme.Word).all()
        return lexemes
    except SQLAlchemyError as e:
        log_error(f"Ошибка при получении списка лексем: {e}", category="lexemes")
        return []
    finally:
        session.close()

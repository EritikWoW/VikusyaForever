from sqlalchemy.exc import SQLAlchemyError
from vikusya.db.connection import SessionLocal
from vikusya.db.models import Lexeme
from vikusya.utils.logger import log_action, log_error

def get_or_create_lexeme(word, part_of_speech=None, gender=None, animate=None, description=None, is_screenshot_trigger=False):
    """
    Получает ID лексемы, если существует, иначе добавляет новую и возвращает её ID.
    """
    session = SessionLocal()
    try:
        lexeme = session.query(Lexeme).filter_by(Word=word).first()
        if lexeme:
            return lexeme.Id

        new_lexeme = Lexeme(
            Word=word,
            PartOfSpeech=part_of_speech,
            Gender=gender,
            Animate=animate,
            Description=description,
            IsScreenshotTrigger=is_screenshot_trigger
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

def get_lexeme_id(word):
    """Возвращает ID лексемы по слову, если есть."""
    session = SessionLocal()
    try:
        lexeme = session.query(Lexeme.Id).filter_by(Word=word).first()
        return lexeme[0] if lexeme else None
    finally:
        session.close()

def get_lexeme_by_id(lexeme_id):
    """Возвращает объект лексемы по ID."""
    session = SessionLocal()
    try:
        return session.query(Lexeme).filter_by(Id=lexeme_id).first()
    finally:
        session.close()

def get_all_lexemes():
    """Возвращает все лексемы."""
    session = SessionLocal()
    try:
        return session.query(
            Lexeme.Id,
            Lexeme.Word,
            Lexeme.PartOfSpeech,
            Lexeme.Gender,
            Lexeme.Animate,
            Lexeme.Description
        ).order_by(Lexeme.Word).all()
    except SQLAlchemyError as e:
        log_error(f"Ошибка при получении списка лексем: {e}", category="lexemes")
        return []
    finally:
        session.close()

def get_screenshot_trigger_lexemes():
    """Возвращает список слов, помеченных как триггеры для скриншота."""
    session = SessionLocal()
    try:
        lexemes = session.query(Lexeme.Word).filter_by(IsScreenshotTrigger=True).all()
        return [lexeme.Word for lexeme in lexemes]
    finally:
        session.close()

def is_screenshot_trigger(word):
    """Проверяет, является ли слово триггером для скриншота."""
    session = SessionLocal()
    try:
        return session.query(Lexeme).filter_by(Word=word, IsScreenshotTrigger=True).first() is not None
    finally:
        session.close()

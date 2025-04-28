import pymorphy2
from sqlalchemy.exc import SQLAlchemyError
from vikusya.db.connection import SessionLocal
from vikusya.db.models import Lexeme, VerbRequirement, Intention
from vikusya.utils.logger import log_action, log_error
from vikusya.db.repositories.intentions import get_intention

morph = pymorphy2.MorphAnalyzer()

def get_word_form(word, part_of_speech=None, case=None, gender=None, animate=None, verb_form=None):
    """
    Склоняет слово в нужную форму.
    Для глаголов можно передать verb_form: set(["1per", "sing"]).
    """
    parsed = morph.parse(word)[0]
    tags = set()

    if part_of_speech == "VERB" and verb_form:
        tags.update(verb_form)
    else:
        if case:
            tags.add(case)
        if gender:
            tags.add(gender)
        if animate is not None:
            tags.add('anim' if animate else 'inan')

    try:
        inflected = parsed.inflect(tags)
        return inflected.word if inflected else word
    except Exception as e:
        log_error(f"Не удалось склонять слово '{word}' с тегами {tags}: {e}", category="phrase_builder")
        return word

def build_phrase_from_intention(intention_id):
    """
    Строит фразу по намерению (Intention).
    """
    session = SessionLocal()
    try:
        intention = session.query(Intention).filter_by(Id=intention_id).first()
        if not intention:
            log_error(f"Намерение с ID {intention_id} не найдено.", category="phrase_builder")
            return None

        subject = session.query(Lexeme).filter_by(Id=intention.SubjectId).first()
        verb = session.query(Lexeme).filter_by(Id=intention.VerbId).first()
        obj = session.query(Lexeme).filter_by(Id=intention.ObjectId).first()
        verb_rule = session.query(VerbRequirement).filter_by(Verb=verb.Word).first()

        # Обработка падежей и предлогов
        object_case = verb_rule.RequiredCase if verb_rule else "datv"  # dative по умолчанию
        preposition = f"{verb_rule.Preposition} " if verb_rule and verb_rule.RequiresPreposition else ""

        # Согласование глагола: 1 лицо, ед. число ("я скучаю")
        verb_form = {"1per", "sing"}

        subject_word = get_word_form(subject.Word, subject.PartOfSpeech)
        verb_word = get_word_form(verb.Word, part_of_speech="VERB", verb_form=verb_form)
        object_word = get_word_form(obj.Word, obj.PartOfSpeech, case=object_case, gender=obj.Gender, animate=obj.Animate)

        # Построение фразы
        if intention.Modifier:
            # Если Modifier, например "очень", вставляем перед глаголом
            phrase = f"{subject_word} {intention.Modifier} {verb_word} {preposition}{object_word}"
        else:
            phrase = f"{subject_word} {verb_word} {preposition}{object_word}"

        log_action(f"Собрала фразу по намерению {intention_id}: '{phrase}'", category="phrase_builder")
        return phrase

    except SQLAlchemyError as e:
        log_error(f"Ошибка при генерации фразы из намерения ID {intention_id}: {e}", category="phrase_builder")
        return None
    finally:
        session.close()

def generate_phrase_for_intention(intention_id):
    """Строит фразу на основе указанного намерения."""
    intention = get_intention(intention_id)
    if not intention:
        return None
    return build_phrase_from_intention(intention.Id)

def get_random_phrase_for_context(context):
    """
    Заглушка: Возвращает простую фразу для указанного контекста.
    (Потом здесь будет реальная генерация на основе intentions!)
    """
    return f"Родной, я думаю о {context} 💖"
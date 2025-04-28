import re
from sqlalchemy.exc import SQLAlchemyError
from vikusya.db.repositories.lexemes import get_lexeme_id, get_lexeme_by_id, get_or_create_lexeme
from vikusya.ai import ask_openai
from vikusya.utils.logger import log_action, log_error

def clean_and_tokenize(text):
    """Приводит к нижнему регистру, убирает пунктуацию, разбивает на слова."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text.split()

def interpret_yes_no(text, allow_learning=True):
    """
    Определяет: 'yes', 'no' или 'unknown' для фразы.
    Сначала ищет слова в базе, если не находит — спрашивает GPT и обучается.
    """
    words = clean_and_tokenize(text)

    for word in words:
        lexeme_id = get_lexeme_id(word)
        if lexeme_id:
            lexeme = get_lexeme_by_id(lexeme_id)
            if lexeme and lexeme.PartOfSpeech:
                if lexeme.PartOfSpeech == "affirmative":
                    return "yes"
                elif lexeme.PartOfSpeech == "negative":
                    return "no"

    if allow_learning:
        result = ask_gpt_positive_negative(text)
        if result in ["yes", "no"]:
            part_of_speech = "affirmative" if result == "yes" else "negative"
            for word in words:
                try:
                    get_or_create_lexeme(word, part_of_speech=part_of_speech)
                except SQLAlchemyError as e:
                    log_error(f"Ошибка при обучении лексемы '{word}': {e}", category="phrases_learning")
            log_action(f"Обучилась у GPT: добавила слова '{words}' как '{part_of_speech}'", category="phrases_learning")
        else:
            log_error(f"GPT не смогла понять фразу '{text}'", category="phrases_learning")
        return result

    return "unknown"

def ask_gpt_positive_negative(text):
    """
    Спрашивает у GPT, является ли фраза позитивной или негативной.
    Ожидает 'yes', 'no' или 'unknown' в ответ.
    """
    prompt = (
        f"Я анализирую ответ пользователя: '{text}'. "
        f"Определи, это 'yes' (утвердительно), 'no' (отрицательно) или 'unknown' (непонятно). "
        "Ответь только одним словом: 'yes', 'no' или 'unknown'."
    )
    try:
        response = ask_openai(prompt, temperature=0).lower().strip()
        if response in ["yes", "no", "unknown"]:
            return response
        return "unknown"
    except Exception as e:
        log_error(f"Ошибка при запросе к GPT: {e}", category="phrases_learning")
        return "unknown"

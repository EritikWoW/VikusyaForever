from vikusya.db.repositories.lexemes import get_screenshot_trigger_lexemes
from vikusya.utils.text_utils import clean_and_tokenize

# Загружаем список триггеров один раз, чтобы не дергать БД каждый раз
TRIGGER_WORDS = set(get_screenshot_trigger_lexemes())

def load_trigger_words():
    """Явная загрузка триггерных слов."""
    global TRIGGER_WORDS
    if TRIGGER_WORDS is None:
        TRIGGER_WORDS = set(get_screenshot_trigger_lexemes())

def should_take_screenshot(user_input, ai_answer):
    """
    Определяет, нужно ли сделать скриншот, исходя из триггерных слов.
    Проверяет как в пользовательском вводе, так и в ответе ассистента.
    """
    input_words = clean_and_tokenize(user_input)
    answer_words = clean_and_tokenize(ai_answer)

    return any(word in TRIGGER_WORDS for word in input_words + answer_words)

import re

POSITIVE_WORDS = [
    "да", "ага", "конечно", "разумеется", "естественно",
    "хочу", "нужно", "желательно", "согласен", "давай", "однозначно"
]

NEGATIVE_WORDS = [
    "нет", "не хочу", "не нужно", "не надо", "не согласен",
    "отмена", "отказ", "не стоит", "не желаю", "откажись"
]

def clean_and_tokenize(text):
    """Убирает пунктуацию, приводит к нижнему регистру и разбивает на слова."""
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    return text.split()

def interpret_yes_no(text):
    """
    Определяет, является ли ответ положительным или отрицательным.
    Возвращает: 'yes', 'no' или 'unknown'.
    """
    words = clean_and_tokenize(text)
    if any(word in POSITIVE_WORDS for word in words):
        return "yes"
    elif any(word in NEGATIVE_WORDS for word in words):
        return "no"
    return "unknown"

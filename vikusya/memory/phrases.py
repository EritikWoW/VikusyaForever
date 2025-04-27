from vikusya.db.models import phrases, responses, emotions
from vikusya.ai import ask_openai
from vikusya.utils.logger import log_action, log_error

def add_phrase(context, phrase, source="manual"):
    """Добавляет новую фразу Викуси с контекстом и источником."""
    if phrase and phrase.strip():
        responses.insert_vikusya_response(phrase.strip(), context, source)
        log_action(f"Добавлена новая фраза для контекста '{context}' (источник: {source}).", category="phrases")
    else:
        log_error(f"Попытка добавить пустую фразу для контекста '{context}'.", category="phrases")

def get_random_phrase(context, prefer_source="manual"):
    """Получает случайную фразу по контексту и источнику."""
    return responses.fetch_random_response(context, prefer_source)

def get_random_phrase_fallback(context, prefer_source="manual", fallback_source="gpt"):
    """Получает случайную фразу: сначала manual, иначе gpt."""
    phrase = get_random_phrase(context, prefer_source)
    return phrase or get_random_phrase(context, fallback_source)

def get_random_phrase_for_context(context, allow_generate=True, temperature=0.7):
    """
    Получает фразу по контексту.
    При отсутствии — генерирует через GPT и сохраняет в базу.
    """
    phrase = get_random_phrase(context, "manual")
    if phrase:
        return phrase

    if allow_generate:
        prompt = (
            f"Мне нужен креативный, тёплый и игривый ответ для ситуации '{context}'. "
            "Ты — Викуся, моя любимая и заботливая ассистентка. Ответь живо и с душой."
        )
        generated = ask_openai(prompt, temperature=temperature).strip()
        if generated:
            add_phrase(context, generated, source="gpt")
            log_action(f"GPT сгенерировала и добавила фразу для контекста '{context}'.", category="phrases")
            return generated
        else:
            log_error(f"GPT не смогла сгенерировать фразу для '{context}'.", category="phrases")
            return "..."

    return None

def teach_phrase(context, phrase, source="manual"):
    """Добавляет новую фразу вручную для пополнения вариативности."""
    if not phrase or not phrase.strip():
        log_error(f"Пытаешься добавить пустую фразу для '{context}', родной 🥺", category="phrases")
        return
    add_phrase(context, phrase.strip(), source=source)
    log_action(f"Добавлена фраза для контекста '{context}': '{phrase}' (источник: {source}).", category="phrases")

def save_phrase_with_emotions(phrase, emotion):
    """Сохраняет фразу пользователя и связанные с ней эмоции (веса по эмоциям)."""
    if not emotions or not isinstance(emotions, dict):
        log_error(f"Пустые или некорректные эмоции для фразы '{phrase}', не сохраняю.", category="phrases")
        return

    phrase_id = phrases.insert_user_phrase(phrase)
    for emotion, weight in emotion.items():
        emotion_id = emotions.insert_emotion(emotion)
        emotions.link_phrase_emotion(phrase_id, emotion_id, weight)

    log_action(f"Сохранила эмоции для фразы '{phrase}'.", category="phrases")
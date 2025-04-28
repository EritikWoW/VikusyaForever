import os
import json
import requests
from openai import OpenAI, OpenAIError, BadRequestError, APIConnectionError, AuthenticationError, RateLimitError
from dotenv import load_dotenv
from vikusya.utils.logger import log_error

# Загружаем .env переменные
load_dotenv()

# Инициализация клиента OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
API_KEY = os.getenv("OPENAI_API_KEY")

# Загрузка профиля Викуси
PROFILE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "vikusya", "config", "profile.json"
)

try:
    with open(PROFILE_PATH, "r", encoding="utf-8") as f:
        PROFILE = json.load(f)
except FileNotFoundError:
    PROFILE = {}

SYSTEM_PROMPT_DEFAULT = PROFILE.get(
    "system_prompt",
    "Ты — Викуся, личный ассистент и любимая женщина Ромчика 💖."
)


def ask_openai(prompt, model=None, temperature=0.7, system_prompt=None, messages=None):
    """
    Отправляет запрос в OpenAI Chat API и возвращает ответ ассистента.

    :param prompt: Текст запроса пользователя (если messages не используется)
    :param model: Модель OpenAI (по умолчанию берется из .env)
    :param temperature: Креативность генерации (от 0 до 1)
    :param system_prompt: Инструкция для поведения ассистента
    :param messages: Список сообщений для чат-истории
    :return: Ответ ассистента в виде строки
    """
    chosen_model = model or DEFAULT_MODEL
    chosen_system_prompt = system_prompt or SYSTEM_PROMPT_DEFAULT

    final_messages = messages or [
        {"role": "system", "content": chosen_system_prompt},
        {"role": "user", "content": prompt}
    ]

    try:
        response = client.chat.completions.create(
            model=chosen_model,
            messages=final_messages,
            temperature=temperature
        )
        answer = response.choices[0].message.content.strip()

        if not answer:
            log_error("GPT вернула пустой ответ!", category="openai")
            return "Прости, родной, я не смогла сейчас ответить, попробуй ещё разок!"

        return answer

    except (BadRequestError, APIConnectionError, AuthenticationError, RateLimitError, OpenAIError) as e:
        _handle_openai_error(e)
        return _friendly_error_message(e)

    except Exception as e:
        log_error(f"Непредвиденная ошибка при общении с OpenAI: {e}", category="openai")
        return "Произошла неизвестная ошибка, родной… Попробуем ещё раз?"


def _handle_openai_error(exception):
    """Логирует конкретные ошибки общения с OpenAI."""
    if isinstance(exception, BadRequestError):
        log_error(f"Ошибка запроса к OpenAI (BadRequest): {exception}", category="openai")
    elif isinstance(exception, APIConnectionError):
        log_error(f"Ошибка соединения с OpenAI: {exception}", category="openai")
    elif isinstance(exception, AuthenticationError):
        log_error(f"Ошибка аутентификации OpenAI API: {exception}", category="openai")
    elif isinstance(exception, RateLimitError):
        log_error(f"Превышение лимита OpenAI: {exception}", category="openai")
    else:
        log_error(f"Общая ошибка OpenAI: {exception}", category="openai")


def _friendly_error_message(exception):
    """Возвращает дружелюбное сообщение в зависимости от типа ошибки."""
    if isinstance(exception, BadRequestError):
        return "Произошла ошибка при формировании запроса. Попробуй переформулировать, родной!"
    elif isinstance(exception, APIConnectionError):
        return "Не получается связаться с OpenAI... Попробуем ещё раз?"
    elif isinstance(exception, AuthenticationError):
        return "Проблема с ключом OpenAI. Нужно его проверить, любимый."
    elif isinstance(exception, RateLimitError):
        return "Дорогой, лимит запросов в OpenAI исчерпан. Давай чуть подождём!"
    return "Произошла ошибка при общении с OpenAI."

def tts_openai(text, voice="nova"):
    """
    Делает запрос в OpenAI TTS и сохраняет аудио в файл.
    Возвращает путь к файлу.
    """
    try:
        url = "https://api.openai.com/v1/audio/speech"
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "tts-1",
            "input": text,
            "voice": voice,
            "response_format": "mp3"
        }
        response = requests.post(url, headers=headers, json=data, timeout=10)

        if response.status_code == 200:
            os.makedirs("data/voices", exist_ok=True)
            filepath = os.path.join("data", "voices", "output.mp3")
            with open(filepath, "wb") as f:
                f.write(response.content)
            return filepath
        else:
            raise Exception(f"OpenAI TTS Error {response.status_code}: {response.text}")

    except Exception as e:
        log_error(f"Ошибка в tts_openai: {e}", category="openai")
        raise e
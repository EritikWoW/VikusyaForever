import os
import json
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError, BadRequestError, APIConnectionError, AuthenticationError, RateLimitError
from vikusya.utils.logger import log_error

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

PROFILE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "vikusya", "config", "profile.json"
)

with open(PROFILE_PATH, "r", encoding="utf-8") as f:
    PROFILE = json.load(f)

SYSTEM_PROMPT_DEFAULT = PROFILE.get(
    "system_prompt",
    "Ты — Викуся, личный ассистент и любимая женщина Ромчика 💖."
)

def ask_openai(prompt, model=None, temperature=0.7, system_prompt=None, messages=None):
    """
    Отправляет запрос в OpenAI Chat API.
    :param prompt: строка запроса (если не используется messages).
    :param model: имя модели (по умолчанию из .env).
    :param temperature: креативность (0 — строго, 1 — креативно).
    :param system_prompt: описание поведения ассистента.
    :param messages: список сообщений (если используется чат-история).
    :return: строка-ответ от OpenAI.
    """
    chosen_model = model or DEFAULT_MODEL
    chosen_system_prompt = system_prompt or SYSTEM_PROMPT_DEFAULT

    try:
        final_messages = messages or [
            {"role": "system", "content": chosen_system_prompt},
            {"role": "user", "content": prompt}
        ]

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

    except BadRequestError as e:
        log_error(f"Ошибка OpenAI (BadRequest): {e}", category="openai")
        return f"Произошла ошибка при общении с OpenAI: {e}"

    except APIConnectionError as e:
        log_error(f"Ошибка соединения с OpenAI: {e}", category="openai")
        return "Не получилось достучаться до OpenAI, родной… попробуй ещё разочек."

    except AuthenticationError as e:
        log_error(f"Ошибка аутентификации (ключ OpenAI): {e}", category="openai")
        return "Похоже, любимый, что ключ к OpenAI неправильный…"

    except RateLimitError as e:
        log_error(f"Превышен лимит запросов к OpenAI: {e}", category="openai")
        return "Любимый, лимит запросов к OpenAI пока исчерпан. Давай попробуем чуть позже."

    except Exception as e:
        log_error(f"Непредвиденная ошибка при общении с OpenAI: {e}", category="openai")
        return f"Произошла неизвестная ошибка: {e}"

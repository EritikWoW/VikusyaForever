# vikusya/vision.py

import os
import pyautogui
import cv2
import pytesseract
from PIL import Image
from dotenv import load_dotenv
from vikusya.generator.phrase_builder import get_random_phrase_for_context
from vikusya.utils.logger import log_action, log_error

load_dotenv()

# Указываем путь к tesseract
pytesseract.pytesseract.tesseract_cmd = os.getenv(
    "TESSERACT_PATH", r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)
OCR_LANG = os.getenv("OCR_LANG", "eng+rus")


def screenshot_and_read():
    """Делает скриншот всего экрана и распознаёт текст через OCR."""
    try:
        os.makedirs("data/screenshots", exist_ok=True)
        screenshot_path = "data/screenshots/fullscreen.png"

        screenshot = pyautogui.screenshot()
        screenshot.save(screenshot_path)
        print("[Викуся]: Сделала скриншот экрана, анализирую...")

        img = cv2.imread(screenshot_path)
        text = pytesseract.image_to_string(img, lang=OCR_LANG)

        if text.strip():
            log_action("Успешно распознала текст на скриншоте", category="vision")
            return text.strip()
        else:
            log_action("Текст на скриншоте не найден или нечитаем", category="vision")
            return None

    except Exception as e:
        log_error(f"Ошибка при создании скриншота и OCR: {e}", category="vision")
        return None


def ocr_image(image_path):
    """Распознаёт текст на переданном изображении."""
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang=OCR_LANG)

        if text.strip():
            log_action(f"Успешно распознала текст с изображения {image_path}", category="vision")
            return text.strip()
        else:
            log_action(f"Текст на изображении {image_path} не найден", category="vision")
            return None

    except Exception as e:
        log_error(f"Ошибка при OCR изображения {image_path}: {e}", category="vision")
        return None


def handle_natural_question(text):
    """Обрабатывает простые естественные вопросы."""
    text = text.lower()

    if "чем занимаешься" in text:
        return get_random_phrase_for_context("what_are_you_doing")
    elif "ты мне что-нибудь скажешь" in text:
        return get_random_phrase_for_context("say_something")

    return None

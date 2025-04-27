# vikusya/vision.py

import os
import pyautogui
import cv2
import pytesseract
from PIL import Image
from dotenv import load_dotenv
from vikusya.memory.phrases import get_random_phrase_for_context

load_dotenv()

# Укажи путь к tesseract, если не в PATH
pytesseract.pytesseract.tesseract_cmd = os.getenv(
    "TESSERACT_PATH", r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)
OCR_LANG = os.getenv("OCR_LANG", "eng+rus")  # Можно задать язык через .env

def screenshot_and_read():
    """
    Делает скриншот всего экрана и распознаёт текст с помощью OCR.
    Возвращает распознанный текст.
    """
    screenshot = pyautogui.screenshot()
    screenshot_path = "data/screenshots/fullscreen.png"
    os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
    screenshot.save(screenshot_path)
    print("[Викуся]: Сделала скриншот экрана, анализирую...")

    img = cv2.imread(screenshot_path)
    text = pytesseract.image_to_string(img, lang=OCR_LANG)

    if text.strip():
        print(f"[Викуся]: Вот что я вижу на экране:\n{text.strip()}")
    else:
        print("[Викуся]: Ничего не смогла распознать, экран чистый или текст неразборчивый.")

    return text.strip()

def ocr_image(image_path):
    """
    Распознаёт текст с изображения по заданному пути.
    Подходит для использования с захватом окон.
    """
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img, lang=OCR_LANG)
    return text.strip()

def select_area_and_read():
    """
    Позволяет выбрать область экрана для OCR.
    Возвращает распознанный текст.
    """
    print("[Викуся]: Выбери область экрана для анализа...")
    region = pyautogui.selectRegion()  # Это гипотетическая функция (заменить на PySimpleGUI или аналог)
    if not region:
        print("[Викуся]: Область не выбрана.")
        return ""

    left, top, width, height = region
    screenshot = pyautogui.screenshot(region=(left, top, width, height))
    screenshot_path = "data/screenshots/selected_area.png"
    os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
    screenshot.save(screenshot_path)

    img = cv2.imread(screenshot_path)
    text = pytesseract.image_to_string(img, lang=OCR_LANG)

    if text.strip():
        print(f"[Викуся]: Вот что я вижу в выбранной области:\n{text.strip()}")
    else:
        print("[Викуся]: В выбранной области ничего не распознала.")

    return text.strip()

def handle_natural_question(text):
    """
    Обрабатывает естественные вопросы и фразы.
    """
    if "чем занимаешься" in text:
        return get_random_phrase_for_context("what_are_you_doing")  # Из базы
    elif "ты мне что-нибудь скажешь" in text:
        return get_random_phrase_for_context("say_something")  # Из базы
    return None

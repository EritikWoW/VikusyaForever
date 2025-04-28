import os
import threading
import pygame
import pyttsx3
from dotenv import load_dotenv
from vikusya.utils.logger import log_action, log_error
from vikusya.ai import ask_openai, tts_openai
from vikusya.generator.phrase_builder import get_random_phrase_for_context

load_dotenv()

# Настройки
TTS_STRATEGY = os.getenv("TTS_STRATEGY", "openai")  # openai или fallback
OPENAI_TTS_VOICE = os.getenv("OPENAI_TTS_VOICE", "nova")

# Контроль воспроизведения
playback_lock = threading.Lock()
stop_playback_event = threading.Event()

def speak(text):
    """
    Главная функция воспроизведения речи.
    """
    stop_current_playback()
    threading.Thread(target=play_voice, args=(text,), daemon=True).start()

def stop_current_playback():
    if playback_lock.locked():
        stop_playback_event.set()

def play_voice(text):
    with playback_lock:
        stop_playback_event.clear()
        try:
            if TTS_STRATEGY == "openai":
                filepath = tts_openai(text, voice=OPENAI_TTS_VOICE)
                play_mp3(filepath)
            else:
                fallback_speak(text)
        except Exception as e:
            log_error(f"Ошибка в воспроизведении речи: {e}", category="speech")
            fallback_speak(text)

def play_mp3(filename):
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        if stop_playback_event.is_set():
            pygame.mixer.music.stop()
            break
    pygame.mixer.quit()

def fallback_speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def speak_contextual(context):
    phrase = get_random_phrase_for_context(context)
    if phrase:
        speak(phrase)
    else:
        fallback_phrase = f"Сейчас я хочу сказать тебе что-то тёплое о {context} 💖."
        generated = ask_openai(fallback_phrase)
        speak(generated)

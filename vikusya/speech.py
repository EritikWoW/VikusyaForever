# vikusya/speech.py

import os
import requests
import pyttsx3
import pygame
import threading
from dotenv import load_dotenv
from vikusya.memory.phrases import get_random_phrase
from vikusya.ai import ask_openai
from vikusya.memory.phrases import add_phrase

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
VOICE = os.getenv("OPENAI_TTS_VOICE", "nova")

# 🟢 Флаги управления воспроизведением
playback_lock = threading.Lock()
stop_playback_event = threading.Event()

def speak(text):
    """
    Основная функция для воспроизведения речи.
    Использует OpenAI TTS (nova) с fallback на pyttsx3.
    Автоматически прерывает текущую озвучку, если начинается новая.
    """
    stop_current_playback()  # 🟥 Останавливаем предыдущую озвучку, если есть

    threading.Thread(target=play_voice, args=(text,), daemon=True).start()

def stop_current_playback():
    """
    Прерывает воспроизведение текущей озвучки.
    """
    if playback_lock.locked():
        stop_playback_event.set()

def play_voice(text):
    """
    Отвечает за генерацию и воспроизведение озвучки (в отдельном потоке).
    """
    with playback_lock:
        stop_playback_event.clear()
        try:
            print(f"[Викуся говорит (OpenAI TTS: {VOICE})]: {text}")
            url = "https://api.openai.com/v1/audio/speech"
            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "tts-1",
                "input": text,
                "voice": VOICE,
                "response_format": "mp3"
            }
            response = requests.post(url, headers=headers, json=data, timeout=10)

            if response.status_code == 200:
                os.makedirs("data/voices", exist_ok=True)
                filename = "data/voices/output.mp3"
                with open(filename, "wb") as f:
                    f.write(response.content)
                play_mp3(filename)
            else:
                raise Exception(f"OpenAI TTS error: {response.status_code} {response.text}")

        except Exception as e:
            print(f"[Викуся переключается на pyttsx3]: {e}")
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
    """
    Запасной метод воспроизведения через pyttsx3.
    """
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def speak_contextual(context):
    phrase = get_random_phrase(context)
    if phrase:
        speak(phrase)
    else:
        base_prompt = f"Придумай фразу для ситуации '{context}' так, как будто говорит любящая ассистентка по имени Викуся."
        generated_phrase = ask_openai(base_prompt)
        add_phrase(context, generated_phrase, source="gpt")
        speak(generated_phrase)

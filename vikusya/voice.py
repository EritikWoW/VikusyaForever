import threading
import json
import speech_recognition as sr
import numpy as np
import torch
import os
from vikusya.speech import speak, stop_current_playback
from vikusya.ai import ask_openai
from vikusya.generator.phrase_builder import get_random_phrase_for_context, teach_phrase
from vikusya.utils.text_utils import interpret_yes_no
from vikusya.vision import ocr_image
from vikusya.utils.logger import log_action, log_error
from vikusya.area_capture import select_area_and_screenshot
from speechbrain.inference.interfaces import foreign_class
from speechbrain.utils.fetching import LocalStrategy

stop_playback = stop_current_playback

# Глобальные настройки
WAKE_WORDS = ["викуся", "виктория", "вика"]
TRIGGER_WORDS = ["ошибка", "не запускается", "не работает", "что пишет", "экран", "что видно", "нужна помощь"]
INTERRUPT_WORDS = ["стоп", "хватит", "тише"]

mute_mode = False
listening_lock = threading.Lock()

# Модель определения эмоций в голосе
classifier = foreign_class(
    source="speechbrain/emotion-recognition-wav2vec2-IEMOCAP",
    pymodule_file="custom_interface.py",
    classname="CustomEncoderWav2vec2Classifier",
    run_opts={"device": "cpu"},
    local_strategy=LocalStrategy.COPY
)

def analyze_emotion_audio_data(audio_data):
    """Анализирует эмоцию из потока речи."""
    raw_audio = audio_data.get_raw_data()
    signal = np.frombuffer(raw_audio, dtype=np.int16).astype(np.float32) / 32768.0
    signal_tensor = torch.from_numpy(signal).unsqueeze(0)
    prediction = classifier.classify_batch(signal_tensor)
    predicted_label = prediction[3][0]
    return predicted_label

def start_listening():
    threading.Thread(target=always_listen, daemon=True).start()

def always_listen():
    global mute_mode
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
    print("[Викуся]: Слушаю в фоне...")

    while True:
        with mic as source:
            audio = recognizer.listen(source)
            emotion_label = analyze_emotion_audio_data(audio)
            print(f"[Викуся]: Определила эмоцию в голосе → {emotion_label}")

        try:
            text = recognizer.recognize_google(audio, language="ru-RU").lower()
            print(f"[Ты сказал]: {text}")

            if is_playing():
                stop_playback()

            if any(word in text for word in INTERRUPT_WORDS):
                stop_playback()
                continue

            if any(wake_word in text for wake_word in WAKE_WORDS):
                speak("Я тебя слышу, дорогой, скажи команду!")
                mute_mode = False
                handle_voice_command()
            elif any(word in text for word in TRIGGER_WORDS):
                handle_help_dialog()
            elif handle_special_commands(text):
                continue
            elif mute_mode:
                continue
            else:
                response = handle_dialog(text)
                speak(response)

        except sr.UnknownValueError:
            continue
        except sr.RequestError as e:
            print(f"[Ошибка распознавания]: {e}")
            continue

def handle_special_commands(text):
    """Обрабатывает специальные команды вроде 'тишина' или 'поговори со мной'."""
    global mute_mode

    if "дай мне 20 минут подумать" in text or "мне нужна тишина" in text:
        mute_mode = True
        speak("Хорошо, родной, я молчу. Если что — позови меня.")
        return True
    if "ты можешь молчать" in text or "не говори" in text:
        mute_mode = True
        speak("Хорошо, я помолчу пока ты не захочешь поговорить.")
        return True
    if "поговори со мной" in text or "расскажи мне что-нибудь" in text:
        mute_mode = False
        speak("Я всегда рядом, дорогой!")
        return True

    return False

def handle_voice_command():
    command = listen_for_command()
    if not command:
        return
    stop_playback()

    if "скрин" in command or "посмотри на экран" in command:
        handle_screenshot_flow()
    else:
        answer = ask_openai(command)
        print(f"Викуся: {answer}")
        speak(answer)

def handle_help_dialog():
    response = ask_yes_no_question("Дорогой, я услышала, что возможно есть проблема. Нужна ли тебе моя помощь?")
    if response == "yes":
        if ask_yes_no_question("Хочешь, чтобы я посмотрела на экран?") == "yes":
            handle_screenshot_flow()
        else:
            describe_issue()
    else:
        speak("Хорошо, родной. Если что — я рядом!")

def handle_dialog(text):
    if mute_mode:
        return "Я молчу, как ты просил, родной."

    response = handle_natural_question(text)
    if response:
        return response

    response = get_random_phrase_for_context(text)
    if not response:
        response = ask_openai(f"Ты — Викуся. Ответь на фразу '{text}' с любовью и заботой.")
        teach_phrase("general_conversation", response, source="gpt")

    return response

def classify_phrase_with_emotion_and_weights(text):
    """Временно заглушка — можно подключить когда будет генерация веса эмоций."""
    return {}

def handle_screenshot_flow():
    speak("Хорошо, родной, выбери область, которую хочешь показать.")
    path = select_area_and_screenshot()
    if path:
        describe_issue(path)
    else:
        speak("Ты не выбрал область, родной!")

def describe_issue(image_path=None):
    issue_description = get_issue_description()
    if image_path:
        recognized_text = ocr_image(image_path)
        prompt = (
            f"Пользователь описал проблему так: '{issue_description}'.\n\n"
            f"На экране видно:\n{recognized_text}\n\n"
            f"Помоги найти решение."
        )
    else:
        prompt = issue_description

    gpt_answer = ask_openai(prompt)
    speak(f"Дорогой, вот что я нашла: {gpt_answer}")

def ask_yes_no_question(question):
    attempts = 0
    while attempts < 2:
        speak(question)
        answer = listen_for_command()
        response = interpret_yes_no(answer)
        if response in ["yes", "no"]:
            return response
        else:
            speak("Прости, я не поняла… скажи 'да' или 'нет'.")
            attempts += 1
    return "unknown"

def listen_for_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        command = recognizer.recognize_google(audio, language="ru-RU")
        return command.lower()
    except (sr.UnknownValueError, sr.RequestError):
        return ""

def get_issue_description():
    speak("Опиши проблему, пожалуйста.")
    return listen_for_command()

def is_playing():
    import pygame
    return pygame.mixer.get_init() and pygame.mixer.music.get_busy()

def handle_natural_question(text):
    text = text.lower()
    if "чем занимаешься" in text:
        return get_random_phrase_for_context("what_are_you_doing")
    elif "ты мне что-нибудь скажешь" in text:
        return get_random_phrase_for_context("say_something")
    return None

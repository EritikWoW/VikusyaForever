import threading
import json
import speech_recognition as sr
from vikusya.speech import speak, stop_current_playback
from vikusya.ai import ask_openai
from vikusya.utils.text_utils import interpret_yes_no
from vikusya.vision import ocr_image
from vikusya.area_capture import select_area_and_screenshot
from vikusya.memory.phrases import get_random_phrase_for_context, teach_phrase, save_phrase_with_emotions
import numpy as np
import torch
from speechbrain.inference.interfaces import foreign_class
from speechbrain.utils.fetching import LocalStrategy

WAKE_WORDS = ["викуся", "виктория", "вика"]
TRIGGER_WORDS = ["ошибка", "не запускается", "не работает", "что пишет", "экран", "что видно", "нужна помощь"]
INTERRUPT_WORDS = ["стоп", "хватит", "тише"]

mute_mode = False

listening_lock = threading.Lock()

classifier = foreign_class(
    source="speechbrain/emotion-recognition-wav2vec2-IEMOCAP",
    pymodule_file="custom_interface.py",  # обязательно скачай этот файл с модели Hugging Face!
    classname="CustomEncoderWav2vec2Classifier",
    run_opts={"device": "cpu"},  # или "cuda", если нужен GPU
    local_strategy=LocalStrategy.COPY  # безопасно для Windows
)


def analyze_emotion_audio_data(audio_data):
    """Анализирует эмоции из AudioData (speech_recognition) без сохранения в файл."""
    raw_audio = audio_data.get_raw_data()
    # SpeechRecognition by default uses 16-bit PCM, mono, 16000 Hz
    signal = np.frombuffer(raw_audio, dtype=np.int16).astype(np.float32) / 32768.0
    signal_tensor = torch.from_numpy(signal).unsqueeze(0)  # Добавляем batch dim

    # Запускаем классификацию
    prediction = classifier.classify_batch(signal_tensor)
    predicted_label = prediction[3][0]
    return predicted_label

def start_listening():
    threading.Thread(target=always_listen, daemon=True).start()

def always_listen():
    global mute_mode  # Объявляем mute_mode как глобальную переменную
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

            # Если ты говоришь любое слово, сразу перебиваем воспроизведение:
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

            # Обработка естественных вопросов
            elif "дай мне 20 минут подумать" in text or "мне нужна тишина" in text:
                mute_mode = True
                speak("Хорошо, дорогой, я помолчу. Если что — позови меня.")
                continue

            elif "ты можешь молчать" in text or "не говори" in text:
                mute_mode = True
                speak("Поняла, дорогой. Буду молчать, пока не позовёшь.")
                continue

            elif "поговори со мной" in text or "расскажи мне что-нибудь" in text:
                mute_mode = False
                speak("Я всегда рядом, дорогой!")

            elif mute_mode:
                continue

            else:
                # Если не в mute_mode — реагируем на диалог
                response = handle_dialog(text)
                speak(response)

        except sr.UnknownValueError:
            continue
        except sr.RequestError as e:
            print(f"[Ошибка распознавания]: {e}")
            continue


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
        screen_response = ask_yes_no_question("Хочешь, чтобы я посмотрела на экран?")
        if screen_response == "yes":
            handle_screenshot_flow()
        elif screen_response == "no":
            issue_description = get_issue_description()
            gpt_answer = ask_openai(issue_description)
            speak(f"Дорогой, вот что я нашла для тебя: {gpt_answer}")
        else:
            speak("Я не поняла твой ответ, родной. Если что — я рядом!")
    elif response == "no":
        speak("Окей, родной, если что — скажи!")
    else:
        speak("Я всё ещё не уверена… Если вдруг понадобится помощь — скажи!")

def handle_dialog(text):
    """
    Обрабатывает диалоговые фразы и решает, что ответить.
    Если в mute_mode — молчит.
    """
    global mute_mode

    # Если фраза в mute_mode — игнорируем её
    if mute_mode:
        return "Я молчу, как ты просил, родной. Позови меня, когда будешь готов."

        # Классификация фразы с использованием GPT для получения эмоций
    emotions = classify_phrase_with_emotion_and_weights(text)
    save_phrase_with_emotions(text, emotions)

    # Если не в mute_mode — реагируем на диалог
    response = handle_natural_question(text)
    if response:
        return response


    # Если нет конкретной реакции, подбираем фразу из базы или GPT
    response = get_random_phrase_for_context(text)
    if not response:
        response = ask_openai(f"Ты — Викуся. Ответь на фразу '{text}' с учётом её стиля: нежная и игривая.")
        teach_phrase("general_conversation", response, source="gpt")

    return response


def classify_phrase_with_emotion_and_weights(text):
    """Запрашивает у GPT эмоции для фразы и возвращает их веса."""
    prompt = f"Оцени эту фразу '{text}' по эмоциям с коэффициентами для каждого состояния. Ответ нужен в формате JSON, без дополнительных описаний, и состояния на английском языке."
    classification = ask_openai(prompt)  # Получаем классификацию от GPT

    try:
        emotions_dict = json.loads(classification)
    except json.JSONDecodeError as e:
        print(f"[Викуся]: Ошибка парсинга эмоций JSON: {e}")
        emotions_dict = {}

    return emotions_dict

def handle_screenshot_flow():
    speak("Хорошо, дорогой, выбери область, которую хочешь показать.")
    path = select_area_and_screenshot()
    if path:
        issue_description = get_issue_description()
        gpt_answer = send_screenshot_and_description(path, issue_description)
        speak(f"Дорогой, вот что я нашла для тебя: {gpt_answer}")
    else:
        speak("Ты не выбрал область, родной!")

def ask_yes_no_question(question):
    attempts = 0
    while attempts < 2:
        speak(question)
        answer = listen_for_command()
        response = interpret_yes_no(answer)
        print(f"[Викуся]: Получен ответ: '{answer}' → интерпретирован как: '{response}'")
        if response in ["yes", "no"]:
            return response
        else:
            speak("Прости, дорогой, я не поняла… скажи, пожалуйста, 'да' или 'нет'.")
            attempts += 1
    speak("Я всё ещё не уверена, дорогой. Если что — я рядом!")
    return "unknown"

def listen_for_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("[Викуся]: Говори команду!")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        command = recognizer.recognize_google(audio, language="ru-RU")
        print(f"[Команда]: {command}")
        return command.lower()
    except sr.UnknownValueError:
        print("[Викуся]: Прости, не расслышала команду...")
        speak("Прости, не расслышала команду...")
        return ""
    except sr.RequestError as e:
        print(f"[Викуся]: Ошибка с сервисом распознавания: {e}")
        return ""

def get_issue_description():
    speak("Опиши, пожалуйста, суть проблемы или ошибку.")
    return listen_for_command()

def send_screenshot_and_description(image_path, description):
    recognized_text = ocr_image(image_path)
    prompt = (f"Пользователь описал проблему так: '{description}'.\n\n"
              f"Вот текст, который был найден на скриншоте:\n"
              f"{recognized_text}\n\n"
              f"Пожалуйста, подскажи, в чём может быть проблема и как её решить.")
    return ask_openai(prompt)

# Проверка, озвучивает ли сейчас Викуся:
def is_playing():
    import pygame
    return pygame.mixer.get_init() and pygame.mixer.music.get_busy()

def handle_natural_question(text):
    """
    Обрабатывает естественные вопросы и фразы.
    """
    if "чем занимаешься" in text:
        return get_random_phrase_for_context("what_are_you_doing")  # Из базы фраз
    elif "ты мне что-нибудь скажешь" in text:
        return get_random_phrase_for_context("say_something")  # Из базы фраз
    return None

stop_playback = stop_current_playback

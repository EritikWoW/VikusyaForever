import torchaudio
from speechbrain.inference.interfaces import foreign_class
from speechbrain.utils.fetching import LocalStrategy
import os

# Загружаем pre-trained модель SpeechBrain
MODEL_PATH = os.getenv("SPEECHBRAIN_MODEL", "speechbrain/emotion-recognition-wav2vec2-IEMOCAP")

classifier = foreign_class(
    source=MODEL_PATH,
    pymodule_file="custom_interface.py",  # Это из репозитория модели!
    classname="CustomEncoderWav2vec2Classifier",  # Кастомный интерфейс модели
    run_opts={"device": "cpu"},  # Если нужен GPU → {"device": "cuda"}
    local_strategy=LocalStrategy.COPY  # Чтобы не ругалось на symlink в Windows
)

# Сопоставляем эмоции (можно подстроить под свои названия)
EMOTION_MAPPING = {
    "angry": "anger",
    "happy": "joy",
    "sad": "sadness",
    "neutral": "neutral",
    "fearful": "fear",
    "disgust": "disgust",
    "surprised": "surprise"
}


def analyze_emotion(audio_path):
    """
    Анализирует аудиофайл и возвращает вектор эмоций.
    """
    out_prob, score, index, text_lab = classifier.classify_file(audio_path)

    mapped = EMOTION_MAPPING.get(text_lab, "neutral")
    emotion_vector = {emotion: 0.0 for emotion in EMOTION_MAPPING.values()}
    emotion_vector[mapped] = 1.0

    print(f"[Викуся]: Определила эмоцию — {mapped}")
    return emotion_vector


# Пример теста:
if __name__ == "__main__":
    test_audio = "test.wav"
    result = analyze_emotion(test_audio)
    print(result)

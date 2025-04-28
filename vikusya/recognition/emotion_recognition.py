import os
import torchaudio
from speechbrain.inference.interfaces import foreign_class
from speechbrain.utils.fetching import LocalStrategy
from vikusya.utils.logger import log_action, log_error

# Загружаем pre-trained модель SpeechBrain
MODEL_PATH = os.getenv("SPEECHBRAIN_MODEL", "speechbrain/emotion-recognition-wav2vec2-IEMOCAP")

classifier = foreign_class(
    source=MODEL_PATH,
    pymodule_file="custom_interface.py",
    classname="CustomEncoderWav2vec2Classifier",
    run_opts={"device": "cpu"},  # Или "cuda" если нужен GPU
    local_strategy=LocalStrategy.COPY
)

# Сопоставление эмоций
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
    try:
        out_prob, score, index, text_lab = classifier.classify_file(audio_path)
        mapped = EMOTION_MAPPING.get(text_lab, "neutral")

        emotion_vector = {emotion: 0.0 for emotion in EMOTION_MAPPING.values()}
        emotion_vector[mapped] = 1.0

        log_action(f"Определила эмоцию '{mapped}' из файла '{audio_path}'", category="recognition")
        return emotion_vector

    except Exception as e:
        log_error(f"Ошибка при анализе эмоций из файла '{audio_path}': {e}", category="recognition")
        return {emotion: 0.0 for emotion in EMOTION_MAPPING.values()}  # Возвращаем пустой вектор

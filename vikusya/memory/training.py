import json
from vikusya.memory.memory import Memory
from vikusya.utils.logger import log_action

TRAINING_FILE = "memory/training_data.json"

def collect_training_data(limit=100):
    """
    Собирает последние взаимодействия из памяти для самообучения.
    Сохраняет их в training_data.json и пишет в лог.
    """
    memory = Memory()
    interactions = memory.recall(limit=limit)
    training_samples = []

    for row in interactions:
        _, timestamp, user_input, vikusya_answer, tags, rating, notes = row
        sample = {
            "timestamp": str(timestamp),
            "user_input": user_input,
            "vikusya_answer": vikusya_answer,
            "tags": tags,
            "rating": rating,
            "notes": notes
        }
        training_samples.append(sample)

    with open(TRAINING_FILE, "w", encoding="utf-8") as f:
        json.dump(training_samples, f, ensure_ascii=False, indent=4)

    log_action(f"Собрала {len(training_samples)} примеров для самообучения и сохранила их в {TRAINING_FILE}", category="training")

if __name__ == "__main__":
    collect_training_data(limit=100)

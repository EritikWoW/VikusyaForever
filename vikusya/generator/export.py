import json
from vikusya.db.repositories.interactions import fetch_interactions
from vikusya.utils.logger import log_action

def export_interactions_for_training(limit=100, export_path="data/training_data.json"):
    interactions = fetch_interactions(limit=limit)
    data = [
        {
            "timestamp": str(i.Timestamp),
            "user_input": i.UserInput,
            "vikusya_answer": i.VikusyaAnswer,
            "tags": i.Tags,
            "rating": i.Rating,
            "notes": i.Notes
        }
        for i in interactions
    ]
    with open(export_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    log_action(f"Экспортировала {len(data)} взаимодействий в {export_path} для анализа 💖", category="training")

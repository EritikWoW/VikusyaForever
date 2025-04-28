from vikusya.db.repositories.interactions import insert_interaction, fetch_interactions
from vikusya.utils.logger import log_action

def remember_interaction(user_input, ai_answer, tags=None, rating=None, notes=None):
    """Сохраняет взаимодействие в базу данных."""
    insert_interaction(user_input, ai_answer, tags, rating, notes)
    log_action(f"Запомнила взаимодействие: {user_input} → {ai_answer}", category="memory")

def recall_interactions(limit=10, tag_filter=None, date_from=None, date_to=None):
    """Извлекает последние взаимодействия из базы данных."""
    return fetch_interactions(limit=limit, tag_filter=tag_filter, date_from=date_from, date_to=date_to)

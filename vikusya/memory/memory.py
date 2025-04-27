from vikusya.db import schema
from vikusya.utils.logger import log_action

class Memory:
    def __init__(self):
        # Таблицы создаются через models (если нужно)
        schema.init_database()

    def remember(self, user_input, vikusya_answer, tags=None, rating=None, notes=None):
        schema.insert_interaction(user_input, vikusya_answer, tags, rating, notes)
        log_action("memory", f"Записала взаимодействие: '{user_input}' → '{vikusya_answer}'")

    def recall(self, limit=10, tag_filter=None, date_from=None, date_to=None):
        rows = schema.fetch_interactions(limit, tag_filter, date_from, date_to)
        log_action("memory", f"Прочитала {len(rows)} записей из памяти (лимит: {limit}, тег: {tag_filter})")
        return rows


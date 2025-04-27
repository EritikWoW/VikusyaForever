from vikusya.db.connection import get_connection
from vikusya.utils.logger import log_action, log_error

def init_database():
    """Создаёт таблицы, если их ещё нет. Логирует только реальные действия."""
    conn = get_connection()
    cursor = conn.cursor()

    tables = {
        "Emotions": """
            CREATE TABLE IF NOT EXISTS Emotions (
                Id SERIAL PRIMARY KEY,
                Name VARCHAR(100) NOT NULL UNIQUE,
                Description TEXT
            );
        """,
        "UserPhrases": """
            CREATE TABLE IF NOT EXISTS UserPhrases (
                Id SERIAL PRIMARY KEY,
                Phrase TEXT NOT NULL UNIQUE
            );
        """,
        "VikusyaResponses": """
            CREATE TABLE IF NOT EXISTS VikusyaResponses (
                Id SERIAL PRIMARY KEY,
                Response TEXT NOT NULL,
                Source VARCHAR(50) DEFAULT 'manual',
                Context VARCHAR(255) NOT NULL DEFAULT 'general',
                CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """,
        "PhraseEmotions": """
            CREATE TABLE IF NOT EXISTS PhraseEmotions (
                PhraseId INT REFERENCES UserPhrases(Id),
                EmotionId INT REFERENCES Emotions(Id),
                Weight FLOAT CHECK (Weight >= 0 AND Weight <= 1),
                PRIMARY KEY (PhraseId, EmotionId)
            );
        """,
        "PhraseResponses": """
            CREATE TABLE IF NOT EXISTS PhraseResponses (
                PhraseId INT REFERENCES UserPhrases(Id),
                ResponseId INT REFERENCES VikusyaResponses(Id),
                PRIMARY KEY (PhraseId, ResponseId)
            );
        """,
        "Interactions": """
            CREATE TABLE IF NOT EXISTS Interactions (
                Id SERIAL PRIMARY KEY,
                Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UserInput TEXT NOT NULL,
                VikusyaAnswer TEXT NOT NULL,
                Tags VARCHAR(255),
                Rating INT,
                Notes TEXT
            );
        """,
        "PositivePhrases": """
            CREATE TABLE IF NOT EXISTS PositivePhrases(
                Id SERIAL PRIMARY KEY,
                Phrase TEXT NOT NULL UNIQUE,
                CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
         """,
        "NegativePhrases": """
            CREATE TABLE IF NOT EXISTS NegativePhrases(
                Id SERIAL PRIMARY KEY,
                Phrase TEXT NOT NULL UNIQUE,
                CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """
    }

    for table_name, create_sql in tables.items():
        try:
            # Проверяем, есть ли таблица ПЕРЕД созданием:
            cursor.execute("""
                           SELECT COUNT(*)
                           FROM information_schema.tables
                           WHERE table_name = %s;
                           """, (table_name.lower(),))
            exists = cursor.fetchone()[0]

            cursor.execute(create_sql)
            conn.commit()

            if exists == 0:
                log_action(f"Создала таблицу '{table_name}'", category="database")
            # Если таблица уже была, ничего не логируем!
        except Exception as e:
            log_error(f"Ошибка при создании таблицы '{table_name}': {e}", category="database")

    cursor.close()
    conn.close()



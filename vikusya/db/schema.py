from vikusya.db.connection import get_connection
from vikusya.utils.logger import log_action, log_error

def init_database():
    """
    Инициализирует структуру БД для Викуси: создает все необходимые таблицы.
    """
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
        "Lexemes": """
            CREATE TABLE IF NOT EXISTS Lexemes (
                Id SERIAL PRIMARY KEY,
                Word VARCHAR(255) NOT NULL UNIQUE,
                PartOfSpeech VARCHAR(50),
                Gender VARCHAR(20),
                Animate BOOLEAN,
                Description TEXT
            );
        """,
        "VerbRequirements": """
            CREATE TABLE IF NOT EXISTS VerbRequirements (
                Id SERIAL PRIMARY KEY,
                Verb VARCHAR(255) NOT NULL UNIQUE,
                RequiresPreposition BOOLEAN DEFAULT FALSE,
                Preposition VARCHAR(50),
                RequiredCase VARCHAR(50)
            );
        """,
        "LexemeEmotionWeights": """
            CREATE TABLE IF NOT EXISTS LexemeEmotionWeights (
                LexemeId INT REFERENCES Lexemes(Id),
                EmotionId INT REFERENCES Emotions(Id),
                Weight FLOAT CHECK (Weight >= 0 AND Weight <= 1),
                PRIMARY KEY (LexemeId, EmotionId)
            );
        """,
        "Intentions": """
            CREATE TABLE IF NOT EXISTS Intentions (
                Id SERIAL PRIMARY KEY,
                SubjectId INT REFERENCES Lexemes(Id),
                VerbId INT REFERENCES Lexemes(Id),
                ObjectId INT REFERENCES Lexemes(Id),
                Modifier TEXT,
                CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """,
        "PositivePhrases": """
            CREATE TABLE IF NOT EXISTS PositivePhrases (
                Id SERIAL PRIMARY KEY,
                Phrase TEXT NOT NULL UNIQUE,
                CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """,
        "NegativePhrases": """
            CREATE TABLE IF NOT EXISTS NegativePhrases (
                Id SERIAL PRIMARY KEY,
                Phrase TEXT NOT NULL UNIQUE,
                CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
        """
    }

    for table_name, create_sql in tables.items():
        try:
            cursor.execute(create_sql)
            log_action(f"Таблица '{table_name}' проверена или создана", category="database")
        except Exception as e:
            log_error(f"Ошибка при создании таблицы '{table_name}': {e}", category="database")

    conn.commit()
    cursor.close()
    conn.close()
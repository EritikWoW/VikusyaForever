import os
from datetime import datetime, timedelta

LOG_DIR = "data/logs"
LOG_RETENTION_DAYS = 3  # Сколько дней храним логи

LOG_LEVELS = {
    "DEBUG": 10,
    "INFO": 20,
    "ERROR": 30
}

CURRENT_LOG_LEVEL = LOG_LEVELS["DEBUG"]  # Можно менять на INFO или ERROR при необходимости

def _get_log_file(category="general"):
    """Формирует путь к лог-файлу по категории."""
    category_path = os.path.join(LOG_DIR, category)
    os.makedirs(category_path, exist_ok=True)
    _cleanup_old_logs(category_path)
    date_str = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(category_path, f"{date_str}.log")

def _format_message(level, message):
    """Форматирует сообщение с текущей датой, временем и уровнем."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"[{timestamp}] [{level}] {message}"

def _write_log(level, message, category="general"):
    if LOG_LEVELS[level] >= CURRENT_LOG_LEVEL:
        log_file = _get_log_file(category)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(_format_message(level, message) + "\n")
        if level == "ERROR":
            print(f"[Викуся]: {_format_message(level, message)}")

# --------------------
# Основные функции логгера:
# --------------------
def log_debug(message, category="general"):
    _write_log("DEBUG", message, category)

def log_action(message, category="general"):
    _write_log("INFO", message, category)

def log_error(message, category="general"):
    _write_log("ERROR", message, category)

def _cleanup_old_logs(category_path):
    """Удаляет лог-файлы старше LOG_RETENTION_DAYS."""
    now = datetime.now()
    for filename in os.listdir(category_path):
        if filename.endswith(".log"):
            try:
                date_part = filename.replace(".log", "")
                file_date = datetime.strptime(date_part, "%Y-%m-%d")
                if (now - file_date).days > LOG_RETENTION_DAYS:
                    file_path = os.path.join(category_path, filename)
                    os.remove(file_path)
                    print(f"[Викуся]: Удалила старый лог: {file_path}")
            except ValueError:
                continue

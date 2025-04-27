import os
from datetime import datetime, timedelta

LOG_DIR = "data/logs"
LOG_RETENTION_DAYS = 3  # Сколько дней храним логи

def _get_log_file(category="general"):
    """Формирует путь к лог-файлу по категории."""
    category_path = os.path.join(LOG_DIR, category)
    os.makedirs(category_path, exist_ok=True)
    _cleanup_old_logs(category_path)  # Чистим старые файлы при каждом вызове
    date_str = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(category_path, f"{date_str}.log")

def _format_message(message):
    """Форматирует сообщение с текущей датой и временем."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"[{timestamp}] {message}"

def log_action(message, category="general"):
    """Записывает обычное действие в лог-файл."""
    log_file = _get_log_file(category)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(_format_message(message) + "\n")

def log_error(message, category="general"):
    """Записывает ошибку в лог-файл и выводит на экран."""
    log_file = _get_log_file(category)
    error_message = _format_message(f"[ОШИБКА]: {message}")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(error_message + "\n")
    print(f"[Викуся]: {error_message}")

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
                # Если имя файла не соответствует дате — пропускаем
                continue

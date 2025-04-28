from plyer import notification
from vikusya.utils.logger import log_action, log_error

def notify(title, message):
    """
    Отправляет локальное уведомление пользователю.
    """
    try:
        notification.notify(
            title=title,
            message=message,
            timeout=10
        )
        log_action(f"Отправила уведомление: '{title}' → '{message}'", category="notification")
    except Exception as e:
        log_error(f"Ошибка при отправке уведомления: {e}", category="notification")

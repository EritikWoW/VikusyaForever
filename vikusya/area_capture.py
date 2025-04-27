import os
from PIL import ImageGrab
import tkinter as tk
from vikusya.utils.logger import log_action, log_error

def select_area_and_screenshot(save_path="data/screenshots/selected_area.png"):
    """Позволяет выбрать область экрана и делает скриншот выделенного участка."""
    try:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        root = tk.Tk()
        root.attributes("-fullscreen", True)
        root.attributes("-alpha", 0.3)
        root.configure(bg="black")

        start_x = start_y = end_x = end_y = 0
        rect_id = None

        canvas = tk.Canvas(root, cursor="cross", bg="black", highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)

        def on_mouse_down(event):
            nonlocal start_x, start_y, rect_id
            start_x, start_y = event.x, event.y
            rect_id = canvas.create_rectangle(start_x, start_y, start_x, start_y, outline="red", width=2)

        def on_mouse_move(event):
            if rect_id:
                canvas.coords(rect_id, start_x, start_y, event.x, event.y)

        def on_mouse_up(event):
            nonlocal end_x, end_y
            end_x, end_y = event.x, event.y
            root.quit()  # Использую quit вместо destroy для чистого выхода

        canvas.bind("<ButtonPress-1>", on_mouse_down)
        canvas.bind("<B1-Motion>", on_mouse_move)
        canvas.bind("<ButtonRelease-1>", on_mouse_up)

        root.mainloop()
        root.destroy()

        # Проверяем, что область действительно выбрана:
        if start_x == end_x or start_y == end_y:
            log_action("Выделение области для скриншота отменено пользователем", category="screenshot")
            return None

        x1, y1 = min(start_x, end_x), min(start_y, end_y)
        x2, y2 = max(start_x, end_x), max(start_y, end_y)
        screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        screenshot.save(save_path)
        log_action(f"Сделала скриншот выделенной области, сохранила в {save_path}", category="screenshot")
        return save_path

    except Exception as e:
        log_error(f"Ошибка при создании скриншота: {e}", category="screenshot")
        return None

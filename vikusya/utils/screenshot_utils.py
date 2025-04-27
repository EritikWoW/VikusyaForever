# Функция для определения, нужно ли делать скриншот
AUTO_SCREEN_TRIGGER_WORDS = [
    "ошибка", "на экране", "не запускается", "что пишет",
    "что видно", "покажи", "покажи экран", "подскажи что там"
]

def should_take_screenshot(user_input, ai_answer):
    input_lower = user_input.lower()
    ai_lower = ai_answer.lower()
    return any(word in input_lower for word in AUTO_SCREEN_TRIGGER_WORDS) or \
           any(word in ai_lower for word in AUTO_SCREEN_TRIGGER_WORDS)

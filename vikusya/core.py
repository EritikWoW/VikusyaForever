import os
from dotenv import load_dotenv
from vikusya.speech import speak, speak_contextual
from vikusya.generator.interaction_service import remember_interaction
from vikusya.ai import ask_openai
from vikusya.vision import screenshot_and_read
from vikusya.voice import start_listening, listen_for_command
from vikusya.utils.text_utils import interpret_yes_no
from vikusya.utils.screenshot_utils import should_take_screenshot, load_trigger_words
from vikusya.db.init_db import init_database
from vikusya.utils.logger import log_action, log_error
from vikusya.db.connection import create_database_if_not_exists, engine

class Vikusya:
    def __init__(self):
        load_dotenv()

        create_database_if_not_exists()

        init_database()

        load_trigger_words()
        start_listening()

        self.api_key = os.getenv("OPENAI_API_KEY")

        log_action("Старт ассистента", category="system")

    def run(self):
        speak_contextual("greeting")
        try:
            while True:
                user_input = input("Ты (ввод): ").strip().lower()

                if user_input in ["выход", "пока", "до свидания"]:
                    speak_contextual("goodbye")
                    log_action("Завершение сессии пользователем", category="system")
                    break

                if not user_input:
                    continue

                speak_contextual("processing")

                # Основная логика ответа
                answer = self.process_input(user_input)

                print(f"Викуся: {answer}")
                speak(answer)

        except KeyboardInterrupt:
            log_action("Ассистент остановлен по Ctrl+C", category="system")
            speak("Хорошо, родной, я ухожу... Буду ждать, когда снова позовёшь меня 💖")
            print("\n[Викуся]: Остановлено.")
        except Exception as e:
            log_error(f"Ошибка в основном цикле: {e}", category="system")
            speak("Ой, родной, что-то пошло не так… Проверь, пожалуйста, логи!")

    def process_input(self, user_input):
        """Обрабатывает вход пользователя, включая помощь с экраном."""
        try:
            answer = ask_openai(user_input)
            remember_interaction(user_input, answer)

            # Проверка: нужно ли делать скриншот
            if should_take_screenshot(user_input, answer):
                if self.ask_yes_no_question("Дорогой, кажется, это важно. Хочешь, я посмотрю на экран?") == "yes":
                    screen_text = screenshot_and_read()
                    if screen_text:
                        problem_prompt = (
                            f"На экране видно следующее:\n\n'{screen_text}'\n\n"
                            f"Подскажи, пожалуйста, в чём ошибка и как её устранить."
                        )
                        gpt_response = ask_openai(problem_prompt)
                        speak(f"Любимый, вот что я нашла для тебя: {gpt_response}")
                        answer += f"\n\n🖼️ Найденное решение:\n{gpt_response}"
                    else:
                        speak("Я сделала скриншот, но не нашла текста. Может быть, экран пустой?")

            return answer

        except Exception as e:
            log_error(f"Ошибка при обработке ввода: {e}", category="system")
            return "Прости, родной, что-то пошло не так."

    def ask_yes_no_question(self, question):
        """Задает вопрос 'да/нет' и интерпретирует ответ."""
        for attempt in range(2):
            speak(question)
            answer = listen_for_command()
            response = interpret_yes_no(answer)
            print(f"[Викуся]: Получен ответ: '{answer}' → интерпретирован как: '{response}'")

            if response in ["yes", "no"]:
                return response

            speak("Прости, дорогой, я не расслышала… скажи 'да' или 'нет'.")

        speak("Я всё ещё не уверена, родной. Если что — я рядом!")
        return "unknown"

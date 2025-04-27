import os
from dotenv import load_dotenv
from vikusya.speech import speak, speak_contextual
from vikusya.memory.memory import Memory
from vikusya.ai import ask_openai
from vikusya.vision import screenshot_and_read
from vikusya.voice import start_listening
from vikusya.utils.text_utils import interpret_yes_no
from vikusya.utils.screenshot_utils import should_take_screenshot
from vikusya.db.schema import init_database
from vikusya.utils.logger import log_action, log_error

class Vikusya:
    def __init__(self):
        load_dotenv()
        init_database()
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.memory = Memory()
        start_listening()
        log_action("Старт ассистента", category="system")

    def run(self):
        speak_contextual("greeting")
        try:
            while True:
                user_input = input("Ты (ввод): ").strip().lower()

                if user_input in ["выход", "пока", "до свидания"]:
                    speak_contextual("goodbye")
                    log_action("Завершение сессии по команде пользователя", category="system")
                    break

                if not user_input:
                    continue

                speak_contextual("processing")

                answer = ask_openai(user_input)
                print(f"Викуся: {answer}")
                self.memory.remember(user_input, answer)

                if should_take_screenshot(user_input, answer):
                    response = self.ask_yes_no_question("Дорогой, я услышала, что это может быть важно. Нужна ли тебе моя помощь?")
                    if response == "yes":
                        screen_response = self.ask_yes_no_question("Хочешь, чтобы я посмотрела на экран?")
                        if screen_response == "yes":
                            result = screenshot_and_read()
                            if result:
                                problem_prompt = (
                                    f"На экране пользователя появилось следующее сообщение:\n\n"
                                    f"'{result}'\n\n"
                                    f"Пожалуйста, опиши, что это за ошибка и как её можно решить."
                                )
                                gpt_help = ask_openai(problem_prompt)
                                speak(f"Любимый, вот что я нашла для тебя: {gpt_help}")
                                answer += f"\n\n🖼️ Я сделала скриншот и нашла решение:\n{gpt_help}"
                            else:
                                speak("Я сделала скриншот, но не нашла текста для анализа. Может быть, окно пустое?")
                        elif screen_response == "no":
                            speak("Хорошо, родной, если что — скажи!")
                        else:
                            speak("Я всё ещё не уверена, дорогой… Если что — я рядом!")

                speak(answer)

        except KeyboardInterrupt:
            log_action("Ассистент остановлен по Ctrl+C", category="system")
            speak("Хорошо, родной, я выхожу... Буду ждать, когда снова позовёшь меня 💖")
            print("\n[Викуся]: Остановлено по твоему желанию.")
        except Exception as e:
            log_error(f"Непредвиденная ошибка в основном цикле: {e}", category="system")
            speak("Ой, родной, что-то пошло не так… Проверь, пожалуйста, логи!")

    def listen_for_text_command(self):
        try:
            from vikusya.voice import listen_for_command
            return listen_for_command()
        except ImportError:
            return input("Ты (ответ): ").lower()

    def ask_yes_no_question(self, question):
        attempts = 0
        while attempts < 2:
            speak(question)
            answer = self.listen_for_text_command()
            response = interpret_yes_no(answer)
            print(f"[Викуся]: Получен ответ: '{answer}' → интерпретирован как: '{response}'")
            if response in ["yes", "no"]:
                return response
            else:
                speak("Прости, дорогой, я не поняла… скажи, пожалуйста, 'да' или 'нет'.")
                attempts += 1
        speak("Я всё ещё не уверена, дорогой. Если что — я рядом!")
        return "unknown"

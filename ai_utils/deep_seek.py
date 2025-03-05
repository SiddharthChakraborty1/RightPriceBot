from ai_utils.managers import AIManager
import ollama
import re


class DeepSeekManager(AIManager):
    def __init__(self):
        super().__init__(model_name="deepseek-r1")

    def eliminate_thinking(self, message: str) -> str:
        return re.sub(
            r"<think>.*?</think>\n*", "", message, flags=re.DOTALL
        ).strip()

    def chat(self, message: str):
        stream = ollama.chat(
            model="deepseek-r1",
            messages=[{"role": "user", "content": message}],
        )
        response = ""
        for chunk in stream:
            if not isinstance(chunk, tuple):  # Handle tuple case
                continue

            key, value = chunk
            if key == "message" and hasattr(value, "content"):
                response = self.eliminate_thinking(
                    value.content
                )  # Extract the actual text response

        return response

from openai import OpenAI
from .base import LLMProvider

class OllamaProvider(LLMProvider):

    def __init__(self):
        self.client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="llama3",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
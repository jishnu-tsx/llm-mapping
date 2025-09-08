from typing import List, Optional
from .gemini import GeminiProvider
from .openai import OpenAIProvider
from .open_router import OpenRouterProvider
from .groq import GroqProvider
from .ollama import OllamaProvider


class GenAIRouter:
    def __init__(self, provider: str, model: str):
        self.provider_name = provider.lower()
        self.model = model

        if self.provider_name == "gemini":
            self.provider = GeminiProvider(model)
        elif self.provider_name == "openai":
            self.provider = OpenAIProvider(model)
        elif self.provider_name == "openrouter":
            self.provider = OpenRouterProvider(model)
        elif self.provider_name == "groqcloud":
            self.provider = GroqProvider(model)
        elif self.provider_name == "local":
            self.provider = OllamaProvider(model)
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def route(self, prompt: str, images: Optional[List[str]] = None) -> Optional[str]:
        return self.provider.generate(prompt, images)

import os
import requests
from typing import List, Optional
from .base import BaseProvider


class GroqProvider(BaseProvider):
    def __init__(self, model: str):
        super().__init__(model)
        self.base_url = "https://api.groq.com/openai/v1"
        self.api_key = os.getenv("GROQCLOUD_API_KEY")

    def generate(
        self, prompt: str, images: Optional[List[str]] = None
    ) -> Optional[str]:
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            contents = [{"type": "text", "text": prompt}]
            if images:
                for img in images:
                    contents.append({"type": "image_url", "image_url": {"url": img}})
            data = {
                "model": self.model,
                "messages": [{"role": "user", "content": contents}],
            }
            r = requests.post(
                f"{self.base_url}/chat/completions", json=data, headers=headers
            )
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"[Groq] Error: {e}")
            return None

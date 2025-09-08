import os
import requests
from typing import List, Optional
from .base import BaseProvider
from utils import convert_image_b64


class OpenRouterProvider(BaseProvider):
    def __init__(self, model: str):
        super().__init__(model)
        self.base_url = "https://openrouter.ai/api/v1"
        self.api_key = os.getenv("OPEN_ROUTER_KEY")

    def generate(
        self, prompt: str, images: Optional[List[str]] = None
    ) -> Optional[str]:
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
            }
            contents = [{"type": "text", "text": prompt}]
            if images:
                for img in images:
                    if os.path.exists(img):  # local path
                        b64_img = convert_image_b64(img)
                        contents.append(
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{b64_img}"
                                },
                            }
                        )
                    else:  # assume it's already a URL
                        contents.append(
                            {"type": "image_url", "image_url": {"url": img}}
                        )
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
            print(f"[OpenRouter] Error: {e}")
            return None

import os
from openai import OpenAI
from typing import List, Optional
from .base import BaseProvider
import base64


def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


class OpenAIProvider(BaseProvider):
    def __init__(self, model: str):
        super().__init__(model)
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def generate(
        self, prompt: str, images: Optional[List[str]] = None
    ) -> Optional[str]:
        try:
            contents = [{"type": "text", "text": prompt}]
            if images:
                for img in images:
                    if os.path.exists(img):  # local path
                        b64_img = encode_image(img)
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
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": contents}],
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"[OpenAI] Error: {e}")
            return None

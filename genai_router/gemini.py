import os
import google.generativeai as genai
from typing import List, Optional
from .base import BaseProvider


class GeminiProvider(BaseProvider):
    def __init__(self, model: str):
        super().__init__(model)
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.client = genai

    def generate(
        self, prompt: str, images: Optional[List[str]] = None
    ) -> Optional[str]:
        try:
            model = self.client.GenerativeModel(self.model)
            image_parts = []
            if images:
                image_parts = [self.client.upload_file(img) for img in images]
            contents = [prompt] + image_parts
            response = model.generate_content(contents)
            return response.text
        except Exception as e:
            print(f"[Gemini] Error: {e}")
            return None

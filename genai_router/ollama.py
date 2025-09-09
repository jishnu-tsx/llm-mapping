import os
import requests
from typing import List, Optional

from utils import convert_to_md
from .base import BaseProvider

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class OllamaProvider(BaseProvider):
    def __init__(self, model: str):
        super().__init__(model)
        self.base_url = os.getenv("OLLAMA_URL")

    def convert_to_markdown(self, image_path: str) -> str:
        """
        Placeholder for image-to-markdown conversion.
        You will implement this logic.
        """
        md_convert_prompt_path = os.path.join(BASE_DIR, "prompts", "md_convert", "v1")
        with open(
            os.path.join(md_convert_prompt_path, "notes_image_convert.md"), "r"
        ) as f:
            notes_convert_prompt = f.read()
        # notes_convert_prompt = notes_convert_prompt.replace("{FY1}", fy_1)
        # notes_convert_prompt = notes_convert_prompt.replace("{FY2}", )
        notes_md = convert_to_md(notes_convert_prompt, [image_path])

        return notes_md

    def generate(
        self, prompt: str, images: Optional[List[str]] = None
    ) -> Optional[str]:
        try:
            markdown_contents = []
            # if images:
            #     for img in images:
            #         md = self.convert_to_markdown(img)
            #         markdown_contents.append(md)

            with open("output.md", "r") as f:
                markdown = f.read()
            markdown_contents.append(markdown)
            full_prompt = prompt + "\n" + "\n\nnotes.md:\n".join(markdown_contents)

            data = {
                "model": self.model,
                "stream": False,
                "messages": [{"role": "user", "content": full_prompt}],
            }
            r = requests.post(self.base_url, json=data)
            r.raise_for_status()
            return r.json().get("message", {}).get("content", "")
        except Exception as e:
            print(f"[Ollama] Error: {e}")
            return None

import base64
import os
import requests
from dotenv import load_dotenv
import google.generativeai as genai
from openai import OpenAI

load_dotenv()


class GenAIRouter:
    def __init__(self, provider: str, model: str):
        """
        Initialize router for a specific provider and model.
        provider: "gemini", "openai", "openrouter", "groqcloud"
        model: provider-specific model name
        """
        self.provider = provider.lower()
        self.model = model

        if self.provider == "gemini":
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            self.client = genai

        elif self.provider == "openai":
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        elif self.provider == "openrouter":
            self.base_url = "https://openrouter.ai/api/v1"
            self.api_key = os.getenv("OPENROUTER_API_KEY")

        elif self.provider == "groqcloud":
            self.base_url = "https://api.groq.com/openai/v1"
            self.api_key = os.getenv("GROQCLOUD_API_KEY")

        elif self.provider == "local":
            self.base_url = os.getenv("OLLAMA_URL")
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def route(self, prompt: str, images: list[str]):
        """
        Route prompt + images to the configured provider + model.
        images: list of image paths or URLs (depending on provider).
        Returns text output or None on error.
        """
        try:
            if self.provider == "gemini":
                model = self.client.GenerativeModel(self.model)
                # Upload each image file
                image_parts = [self.client.upload_file(img) for img in images]
                response = model.generate_content([prompt] + image_parts)
                return response.text

            elif self.provider == "openai":
                # OpenAI expects "content" as a list of parts
                contents = [{"type": "text", "text": prompt}]
                for img in images:
                    contents.append({"type": "image_url", "image_url": {"url": img}})
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": contents}],
                )
                return response.choices[0].message.content

            elif self.provider == "local":
                try:
                    # Encode images (assuming they are file paths here)
                    encoded_images = []
                    for img_path in images:
                        with open(img_path, "rb") as f:
                            encoded_images.append(
                                base64.b64encode(f.read()).decode("utf-8")
                            )

                    data = {
                        "model": self.model,  # e.g. "gemma3:4b"
                        "stream": False,
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt,
                                "images": encoded_images,  # base64 list
                            }
                        ],
                    }

                    r = requests.post(self.base_url, json=data)
                    r.raise_for_status()
                    return r.json().get("message", {}).get("content", "")
                except Exception as e:
                    print(f"Error calling local Ollama API: {e}")
                    return None

            elif self.provider == "openrouter":
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "HTTP-Referer": "http://localhost",  # Optional but recommended
                }
                contents = [{"type": "text", "text": prompt}]
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

            elif self.provider == "groqcloud":
                headers = {"Authorization": f"Bearer {self.api_key}"}
                contents = [{"type": "text", "text": prompt}]
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
            print(f"Error calling {self.provider} API: {e}")
            return None

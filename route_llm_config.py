import os
from routellm.controller import Controller
import yaml
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold


load_dotenv()

GEMINI_KEY = os.getenv("GOOGLE_API_KEY")

# class LLMRouter:
#     def __init__(self):
#         with open("llm_config.yaml", "r") as f:
#             config = yaml.safe_load(f)
# from routellm.controller import Controller


class LLMRouter:
    def __init__(self):
        # Configure Google's official client
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.client = genai

        # Define your model preferences
        self.strong_model = "gemini-2.5-flash"  # Note: check current available models
        self.weak_model = "gemini-1.5-flash"

    def route(self, prompt, images=None):
        """Send prompt + images to Google Gemini"""
        try:
            model = genai.GenerativeModel(self.strong_model)

            if images:
                # Handle image inputs
                image_parts = [
                    genai.upload_file(img) for img in images
                ]  # Assuming images are file paths
                contents = [prompt] + image_parts
                response = model.generate_content(contents)
            else:
                # Text-only prompt
                response = model.generate_content(prompt)

            return response.text

        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return None

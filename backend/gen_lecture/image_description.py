import base64
import os
from typing import Optional

import google.generativeai as genai
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


class ImageDescriptionGenerator:
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro-vision')

    def generate_description(self, image_data: bytes, mime_type: str = "image/jpeg") -> Optional[str]:
        """
        Generate description for an image using Google Gemini API

        Args:
            image_data: Raw image data in bytes
            mime_type: MIME type of the image (default: image/jpeg)

        Returns:
            str: Generated description or None if generation fails
        """
        try:
            # Convert image to base64
            image_parts = [
                {
                    "mime_type": mime_type,
                    "data": base64.b64encode(image_data).decode('utf-8')
                }
            ]

            prompt_parts = [
                "Describe this image in detail. Focus on the main elements, their arrangement, and any text or important visual information.",
                image_parts[0]
            ]

            response = self.model.generate_content(prompt_parts)
            return response.text

        except Exception as e:
            print(f"Error generating image description: {str(e)}")
            return None

import os
from typing import Optional

from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


class ImageDescriptionGenerator:
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        self.client = genai.Client(api_key=GEMINI_API_KEY)

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
            response = self.client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=[
                    "Describe this image in detail. Focus on the main elements, their arrangement, and any text or important visual information.",
                    types.Part.from_bytes(data=image_data, mime_type=mime_type)
                ]
            )
            return response.text
        except Exception as e:
            print(f"Error generating image description: {str(e)}")
            return None

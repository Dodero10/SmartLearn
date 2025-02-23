import os
import google.generativeai as genai
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class ImageDescriptionGenerator:
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        # Configure the Gemini API with the API key
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Create the model
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",  # You can change this to your desired model
            generation_config={
                "temperature": 1,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
                "response_mime_type": "text/plain",
            },
            system_instruction="Bạn là một người miêu tả các hình ảnh và bảng biểu trong học tập. Bạn hãy mô tả chi tiết hình ảnh đó viết về gì như thế nào sao cho một người chỉ cần qua miêu tả của bạn mà hiểu hết được trong hình có những gì và viết về kiến thức nào."
        )

    def generate_description(self, image_path: str, mime_type: str = "image/jpeg") -> Optional[str]:
        """
        Generate description for an image using Google Gemini API

        Args:
            image_path: Path to the image file
            mime_type: MIME type of the image (default: image/jpeg)

        Returns:
            str: Generated description or None if generation fails
        """
        try:
            # Upload the image to Gemini
            uploaded_file = genai.upload_file(image_path, mime_type=mime_type)
            print(f"Uploaded file '{uploaded_file.display_name}' as: {uploaded_file.uri}")

            # Start chat session with the model to generate the description
            chat_session = self.model.start_chat(
                history=[
                    {
                        "role": "user",
                        "parts": [
                            uploaded_file,
                            "Bạn hãy miêu tả hình ảnh sau. Chỉ trả về miêu tả của hình ảnh thôi nhé"
                        ]
                    }
                ]
            )

            # Send the request to generate the description
            response = chat_session.send_message("Bạn hãy miêu tả hình ảnh sau. Chỉ trả về miêu tả của hình ảnh thôi nhé")
            return response.text

        except Exception as e:
            print(f"Error generating image description: {str(e)}")
            return None

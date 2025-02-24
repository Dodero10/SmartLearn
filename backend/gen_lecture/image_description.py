import io
import os
from typing import List, Optional, Union

import google.generativeai as genai
from dotenv import load_dotenv

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

    def generate_description(self, image_data: Union[str, bytes], mime_type: str = "image/jpeg") -> Optional[str]:
        """
        Generate description for an image using Google Gemini API

        Args:
            image_data: Either path to image file (str) or image bytes data (bytes)
            mime_type: MIME type of the image (default: image/jpeg)

        Returns:
            str: Generated description or None if generation fails
        """
        try:
            # Handle both file path and bytes data
            if isinstance(image_data, str):
                uploaded_file = genai.upload_file(
                    image_data, mime_type=mime_type)
            else:
                # Create a temporary file-like object for bytes data
                image_stream = io.BytesIO(image_data)
                uploaded_file = genai.upload_file(
                    image_stream, mime_type=mime_type)

            print(f"Uploaded file to Gemini API successfully")

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
            response = chat_session.send_message(
                "Bạn hãy miêu tả hình ảnh sau. Chỉ trả về miêu tả của hình ảnh thôi nhé")
            return response.text

        except Exception as e:
            print(f"Error generating image description: {str(e)}")
            return None

    def generate_table_description(self, columns: List[str], rows: List[List[str]]) -> Optional[str]:
        """
        Generate description for a table using Google Gemini API

        Args:
            columns: List of column headers
            rows: List of rows, each row is a list of cell values

        Returns:
            str: Generated description or None if generation fails
        """
        try:
            # Format table data as a string
            table_str = "Bảng dữ liệu:\n\n"
            # Add headers
            table_str += " | ".join(columns) + "\n"
            table_str += "-" * (len(table_str)) + "\n"
            # Add rows
            for row in rows:
                table_str += " | ".join(str(cell) for cell in row) + "\n"

            # Start chat session with the model to generate the description
            chat_session = self.model.start_chat(
                history=[
                    {
                        "role": "user",
                        "parts": [
                            "Hãy mô tả nội dung và ý nghĩa của bảng dữ liệu sau:\n\n" + table_str
                        ]
                    }
                ]
            )

            # Send the request to generate the description
            response = chat_session.send_message(
                "Hãy mô tả nội dung và ý nghĩa của bảng dữ liệu này một cách chi tiết và dễ hiểu")
            return response.text

        except Exception as e:
            print(f"Error generating table description: {str(e)}")
            return None

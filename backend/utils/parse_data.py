import fitz
from PIL import Image
import io
import base64
from io import BytesIO
import requests
import time
import re
from utils.gpt_call import ChatGPTGen

class ParseHandler():
    _instance = None
    prompt_system = """You are an AI assistant that processes images containing educational content. Your task is to transcribe the content from the image into markdown format with the following rules:

        1. Use `#` for **main topics** (e.g., book titles, law names, main subjects).
        2. Use `##` for **sections** (e.g., "Chapter 1", "Lesson 2", "Example 3").
        3. Use `###` for **subsections** (e.g., "Definitions", "Theorems", "Proofs").
        4. Use `####` for **specific points** (e.g., "Article 1", "Step 2").
        5. Use `-` for **bullet points** and `1.`, `2.`, `3.` for **numbered lists**.
        6. If an equation is present, format it using LaTeX inside `$$ ... $$`.
        7. Format tables in Markdown while keeping text in the correct cells.
        8. Only respond with the markdown content, without any additional explanation or description.
        9. Do not include ```markdown\n in the response.
        """

    @staticmethod
    def get_instance(api_key):
        """ Static access method. """
        if not ParseHandler._instance:
            ParseHandler._instance = ParseHandler(api_key)
        return ParseHandler._instance

    def __init__(self, api_key) -> None:
        self.api_key = api_key

    def pdf_to_images(self, file_stream, pdf_path, zoom_x=2.0, zoom_y=2.0):
        pdf_document = fitz.open(stream=file_stream, filetype="pdf")
        images = []
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            mat = fitz.Matrix(zoom_x, zoom_y)
            pix = page.get_pixmap(matrix=mat)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            images.append(img)
        image_base64s = []

        for image in images:
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            image_bytes = buffered.getvalue()
            image_base64s.append(base64.b64encode(image_bytes).decode("utf-8"))
        print("số trang: ",len(image_base64s))
        return image_base64s

    def parse_pdf(self, image_base64s, file_name):
        chatGPTGen=ChatGPTGen()
        content=""
        for i in range(0, len(image_base64s)):
            messages=[
                    {
                        "role": "system",
                        "content": [
                            {
                                "type": "text",
                                "text": self.prompt_system
                            },
                        ]
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Transcribe the content from this image into markdown format"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64s[i]}"
                                }
                            }
                        ]
                    }
                ]

            response = chatGPTGen.default_chat_completion(messages=messages)
            content+="\n"
            content+=response

            print(content)
        return content
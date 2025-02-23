import os
from typing import List, Tuple

from dotenv import load_dotenv
from openai import OpenAI

from .models import LectureMetadata

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class ScriptGenerator:
    def __init__(self, lecture_metadata: LectureMetadata):
        self.lecture_metadata = lecture_metadata
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def generate_script(self) -> Tuple[str, List[str]]:
        """Generate a lecture script from slide metadata

        Returns:
            Tuple[str, List[str]]: (full script, list of individual slide scripts)
        """
        script_parts = []
        slide_scripts = []

        for idx, slide in enumerate(self.lecture_metadata.slides):
            prompt = (
                f"Hãy tạo script bài giảng cho slide {slide.slide_number}.\n"
                f"Tiêu đề slide: {slide.title}\n"
                f"Nội dung slide: {slide.text_content}\n"
            )

            if slide.images:
                prompt += "Mô tả hình ảnh trong slide:\n"
                for img in slide.images:
                    if img.description:
                        prompt += f"- {img.description}\n"

            if slide.tables:
                prompt += "Các bảng dữ liệu trong slide:\n"
                for table in slide.tables:
                    if table.description:
                        prompt += f"- {table.description}\n"

            if idx + 1 < len(self.lecture_metadata.slides):
                next_slide = self.lecture_metadata.slides[idx + 1]
                prompt += f"\nSau khi giải thích slide này, hãy thêm câu chuyển tiếp tự nhiên sang slide tiếp theo với tiêu đề '{next_slide.title}'."

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Bạn là một giảng viên chuyên nghiệp. Nhiệm vụ của bạn là tạo ra script bài giảng từ nội dung của các slide. Script cần rõ ràng, mạch lạc và tự nhiên như đang giảng bài."
                    },
                    {"role": "user", "content": prompt}
                ]
            )

            slide_script = response.choices[0].message.content.strip()

            slide_scripts.append(slide_script)

            script_parts.append(
                f"=== Slide {slide.slide_number}: {slide.title} ===\n")
            script_parts.append(slide_script)
            script_parts.append("\n---\n")

        full_script = "\n".join(script_parts)

        self.lecture_metadata.script = full_script

        return full_script, slide_scripts

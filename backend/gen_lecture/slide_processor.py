import io
from typing import List

import pdfplumber
from PIL import Image as PILImage

from .image_description import ImageDescriptionGenerator
from .models import Image, LectureMetadata, SlideMetadata, Table


class SlideProcessor:
    def __init__(self, pdf_data: bytes, filename: str):
        self.pdf_data = pdf_data
        self.filename = filename
        self.image_generator = ImageDescriptionGenerator()

    def extract_text_from_page(self, page) -> tuple[str, str]:
        """Extract text from PDF page"""
        text = page.extract_text()
        if not text:
            return "Không có tiêu đề", ""

        lines = text.split('\n')
        title = lines[0] if lines else "Không có tiêu đề"
        content = '\n'.join(lines[1:]) if len(lines) > 1 else ""

        return title, content

    def extract_tables_from_page(self, page) -> List[Table]:
        """Extract tables from PDF page"""
        tables_data = page.extract_tables()
        tables = []

        for table_data in tables_data:
            if table_data and len(table_data) > 1:  # Has header and data
                headers = table_data[0]
                rows = table_data[1:]
                table = Table(
                    columns=headers,
                    rows=rows
                )
                tables.append(table)

        return tables

    def extract_images(self, page) -> List[Image]:
        """Extract images from PDF page"""
        images = []

        # Extract images from the page
        for image in page.images:
            try:
                # Get image data
                image_bytes = image['stream'].get_data()

                # Convert image stream to proper format using PIL
                img = PILImage.open(io.BytesIO(image_bytes))

                # Convert to RGB if necessary (handles CMYK images)
                if img.mode in ['CMYK', 'P']:
                    img = img.convert('RGB')

                # Save to bytes in JPEG format
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='JPEG')
                img_byte_arr = img_byte_arr.getvalue()

                # Generate description using Gemini
                description = self.image_generator.generate_description(
                    img_byte_arr)

                # Create Image object
                image_obj = Image(
                    data=img_byte_arr,
                    format='JPEG',
                    description=description
                )
                images.append(image_obj)

            except Exception as e:
                print(f"Error processing image: {str(e)}")
                continue

        return images

    def process_slides(self) -> LectureMetadata:
        """Process PDF slides and extract metadata"""
        pdf_stream = io.BytesIO(self.pdf_data)

        slide_metadata_list = []
        with pdfplumber.open(pdf_stream) as pdf:
            for i, page in enumerate(pdf.pages):
                # Extract text
                title, text_content = self.extract_text_from_page(page)

                # Extract tables
                tables = self.extract_tables_from_page(page)

                # Extract images (if needed)
                images = self.extract_images(page)

                # Clean up text content
                text_content = self._clean_text(text_content)

                # Create slide metadata
                slide_metadata = SlideMetadata(
                    slide_number=i + 1,
                    title=title,
                    text_content=text_content,
                    images=images,
                    tables=tables
                )
                slide_metadata_list.append(slide_metadata)

        # Create lecture metadata
        lecture_metadata = LectureMetadata(
            filename=self.filename,
            total_slides=len(slide_metadata_list),
            slides=slide_metadata_list
        )

        return lecture_metadata

    def _clean_text(self, text: str) -> str:
        """Clean up extracted text"""
        # Remove multiple newlines
        text = '\n'.join(line.strip()
                         for line in text.split('\n') if line.strip())
        # Remove multiple spaces
        text = ' '.join(text.split())
        return text

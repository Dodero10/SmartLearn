import io
from datetime import datetime
from typing import List

import fitz  # PyMuPDF
import pdfplumber
from config.minio_client import bucket_name_slide, minio_client
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

    def extract_images(self, page_num: int, slide_name: str) -> List[Image]:
        """Extract images from PDF page using PyMuPDF"""
        images = []

        pdf_document = fitz.open(
            stream=io.BytesIO(self.pdf_data), filetype="pdf")
        try:
            page = pdf_document[page_num]
            image_list = page.get_images()

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            folder_name = f"{slide_name}_{timestamp}"

            # Iterate through images on the page
            for img_index, img_info in enumerate(image_list):
                try:
                    # Get image data
                    xref = img_info[0]  # image reference number
                    base_image = pdf_document.extract_image(xref)
                    image_bytes = base_image["image"]

                    # Convert bytes to BytesIO for PIL
                    img_io = io.BytesIO(image_bytes)
                    img = PILImage.open(img_io)
                    if img.mode in ['CMYK', 'P']:
                        img = img.convert('RGB')

                    # Save to bytes for storage
                    output_io = io.BytesIO()
                    img.save(output_io, format='JPEG', quality=95)
                    img_byte_arr = output_io.getvalue()

                    # Save image to Minio
                    image_filename = f"slide_{page_num + 1}_{img_index + 1}.jpg"
                    minio_path = f"{folder_name}/{image_filename}"

                    minio_client.put_object(
                        bucket_name=bucket_name_slide,
                        object_name=minio_path,
                        data=io.BytesIO(img_byte_arr),
                        length=len(img_byte_arr),
                        content_type="image/jpeg"
                    )

                    # # Generate description using Gemini
                    # description = self.image_generator.generate_description(
                    #     img_byte_arr)

                    # Create Image object
                    image_obj = Image(
                        data=img_byte_arr,
                        format='JPEG',
                        # description=description
                    )
                    images.append(image_obj)

                except Exception as e:
                    print(
                        f"Error processing image {img_index} on page {page_num + 1}: {str(e)}")
                    continue

        except Exception as e:
            print(f"Error processing page {page_num + 1}: {str(e)}")
        finally:
            pdf_document.close()

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

                # Create slide name with timestamp
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                slide_name = f"slide_{i + 1}_{timestamp}"

                # Extract images and save to MinIO
                images = self.extract_images(i, slide_name)

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

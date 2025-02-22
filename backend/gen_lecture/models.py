import base64
from typing import List, Optional

from pydantic import BaseModel, validator


class Table(BaseModel):
    rows: List[List[str]]
    columns: List[str]
    description: Optional[str] = None


class Image(BaseModel):
    data: str  # base64 encoded image data
    format: str
    description: Optional[str] = None

    @validator('data')
    def encode_image_data(cls, v):
        """Convert bytes to base64 string if needed"""
        if isinstance(v, bytes):
            return base64.b64encode(v).decode('utf-8')
        return v


class SlideMetadata(BaseModel):
    slide_number: int
    title: str
    text_content: str
    images: List[Image] = []
    tables: List[Table] = []
    description: Optional[str] = ""


class LectureMetadata(BaseModel):
    filename: str
    total_slides: int
    slides: List[SlideMetadata]
    script: Optional[str] = None
    audio_path: Optional[str] = None

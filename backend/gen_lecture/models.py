import base64
from typing import List, Optional

from pydantic import BaseModel, field_validator


class Table(BaseModel):
    rows: List[List[str]]
    columns: List[str]
    description: Optional[str] = None


class Image(BaseModel):
    path: str  # path in MinIO
    format: str
    description: Optional[str] = None


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

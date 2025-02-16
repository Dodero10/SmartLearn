from typing import List, Optional

from pydantic import BaseModel


class Table(BaseModel):
    rows: List[List[str]]
    columns: List[str]

class Image(BaseModel):
    data: bytes
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
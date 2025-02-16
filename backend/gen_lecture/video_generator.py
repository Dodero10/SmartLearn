import io
import os
import tempfile
from typing import List

import cv2
import numpy as np
from pdf2image import convert_from_bytes
from pydub import AudioSegment

from .models import LectureMetadata


class VideoGenerator:
    def __init__(self, lecture_metadata: LectureMetadata, pdf_data: bytes, audio_data: bytes):
        self.lecture_metadata = lecture_metadata
        self.pdf_data = pdf_data
        self.audio_data = audio_data
        self.fps = 24
        
    def _add_text_to_image(self, image: np.ndarray, text: str) -> np.ndarray:
        """Add text overlay to image"""
        height, width = image.shape[:2]
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        thickness = 2
        color = (255, 255, 255)  # White text
        
        # Add black background for text
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        text_x = width - text_size[0] - 10
        text_y = height - 10
        
        # Draw black background
        cv2.rectangle(
            image,
            (text_x - 5, text_y + 5),
            (text_x + text_size[0] + 5, text_y - text_size[1] - 5),
            (0, 0, 0),
            -1
        )
        
        # Draw text
        cv2.putText(
            image,
            text,
            (text_x, text_y),
            font,
            font_scale,
            color,
            thickness
        )
        
        return image
    
    def _estimate_slide_durations(self, audio_length: float) -> List[float]:
        """Estimate duration for each slide based on text content length"""
        total_text_length = sum(len(slide.text_content) for slide in self.lecture_metadata.slides)
        durations = []
        
        for slide in self.lecture_metadata.slides:
            # Calculate duration proportionally to text length
            text_length = len(slide.text_content)
            duration = (text_length / total_text_length) * audio_length
            # Ensure minimum duration of 3 seconds per slide
            duration = max(duration, 3.0)
            durations.append(duration)
            
        return durations
    
    def generate_video(self) -> bytes:
        """Generate lecture video combining slides and audio"""
        try:
            # Create temporary files
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as video_tmp, \
                 tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as audio_tmp:
                
                video_path = video_tmp.name
                audio_tmp.write(self.audio_data)
                audio_path = audio_tmp.name
                
                # Get audio duration
                audio = AudioSegment.from_mp3(audio_path)
                audio_duration = len(audio) / 1000.0  # Convert to seconds
                
                # Convert PDF to images
                slides = convert_from_bytes(self.pdf_data, fmt='png', dpi=150)  # Lower DPI for efficiency
                
                # Calculate durations
                durations = self._estimate_slide_durations(audio_duration)
                
                # Get dimensions from first slide
                height, width = np.array(slides[0]).shape[:2]
                
                # Initialize video writer
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(
                    video_path,
                    fourcc,
                    self.fps,
                    (width, height)
                )
                
                # Process each slide
                for i, (slide, duration) in enumerate(zip(slides, durations)):
                    # Convert PIL Image to OpenCV format
                    img = cv2.cvtColor(np.array(slide), cv2.COLOR_RGB2BGR)
                    
                    # Add slide number
                    img = self._add_text_to_image(
                        img,
                        f"Slide {i+1}/{len(slides)}"
                    )
                    
                    # Write frames for duration
                    n_frames = int(duration * self.fps)
                    for _ in range(n_frames):
                        out.write(img)
                
                # Release video writer
                out.release()
                
                # Combine video and audio using ffmpeg
                output_path = video_path.replace('.mp4', '_with_audio.mp4')
                os.system(f'ffmpeg -y -i {video_path} -i {audio_path} -c:v copy -c:a aac {output_path}')
                
                # Read final video
                with open(output_path, 'rb') as f:
                    video_data = f.read()
                
                # Clean up temporary files
                os.unlink(video_path)
                os.unlink(audio_path)
                os.unlink(output_path)
                
                return video_data
                
        except Exception as e:
            raise Exception(f"Error generating video: {str(e)}") 
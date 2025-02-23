import io
import os
import tempfile
from typing import List, Tuple

import cv2
import numpy as np
from pdf2image import convert_from_bytes
from pydub import AudioSegment

from .models import LectureMetadata


class VideoGenerator:
    def __init__(self, lecture_metadata: LectureMetadata, pdf_data: bytes, audio_files: List[Tuple[str, bytes]]):
        self.lecture_metadata = lecture_metadata
        self.pdf_data = pdf_data
        self.audio_files = audio_files
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

    def generate_video(self) -> bytes:
        """Generate lecture video combining slides and audio"""
        try:
            # Create temporary directory for audio files
            with tempfile.TemporaryDirectory() as temp_dir:
                video_path = os.path.join(temp_dir, 'output.mp4')
                combined_audio_path = os.path.join(temp_dir, 'combined.mp3')

                # Convert PDF to images
                slides = convert_from_bytes(self.pdf_data, fmt='png', dpi=150)

                # Validate number of slides matches number of audio files
                if len(slides) != len(self.audio_files):
                    raise ValueError(
                        f"Number of slides ({len(slides)}) does not match number of audio files ({len(self.audio_files)})")

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

                # Process audio files and create video frames
                audio_segments = []
                total_frames = 0
                frame_timings = []  # Store when to change slides

                # First pass: calculate total duration and frame timings
                for i, (_, audio_data) in enumerate(self.audio_files):
                    try:
                        # Save and load audio segment
                        audio_path = os.path.join(temp_dir, f'audio_{i}.mp3')
                        with open(audio_path, 'wb') as f:
                            f.write(audio_data)
                        audio_segment = AudioSegment.from_mp3(audio_path)
                        audio_segments.append(audio_segment)

                        # Calculate frames needed for this segment
                        duration = len(audio_segment) / \
                            1000.0  # Convert to seconds
                        n_frames = int(duration * self.fps)
                        total_frames += n_frames
                        # Store frame number when to change slide
                        frame_timings.append((total_frames, i))
                    except Exception as e:
                        raise Exception(
                            f"Error processing audio file {i}: {str(e)}")

                if not audio_segments:
                    raise ValueError(
                        "No audio segments were processed successfully")

                # Combine all audio segments
                try:
                    combined_audio = audio_segments[0]
                    for segment in audio_segments[1:]:
                        combined_audio += segment
                    combined_audio.export(combined_audio_path, format='mp3')
                except Exception as e:
                    raise Exception(
                        f"Error combining audio segments: {str(e)}")

                # Second pass: generate video frames
                current_frame = 0
                current_slide_idx = 0

                # Generate frames for each timing point
                while current_frame < total_frames:
                    try:
                        # Find which slide to show
                        next_slide_found = False
                        for end_frame, slide_idx in frame_timings:
                            if current_frame < end_frame:
                                current_slide_idx = slide_idx
                                next_slide_found = True
                                break

                        if not next_slide_found:
                            # Show last slide if no timing found
                            current_slide_idx = len(slides) - 1

                        # Ensure slide index is valid
                        if current_slide_idx >= len(slides):
                            raise ValueError(
                                f"Invalid slide index {current_slide_idx} for {len(slides)} slides")

                        # Convert current slide to video frame
                        slide = slides[current_slide_idx]
                        img = cv2.cvtColor(np.array(slide), cv2.COLOR_RGB2BGR)

                        # Add slide number and total
                        img = self._add_text_to_image(
                            img,
                            f"Slide {current_slide_idx + 1}/{len(slides)}"
                        )

                        # Write frame
                        out.write(img)
                        current_frame += 1
                    except Exception as e:
                        raise Exception(
                            f"Error generating frame {current_frame}: {str(e)}")

                # Release video writer
                out.release()

                # Combine video and audio using ffmpeg
                output_path = os.path.join(temp_dir, 'final_output.mp4')
                ffmpeg_cmd = f'ffmpeg -y -i {video_path} -i {combined_audio_path} -c:v copy -c:a aac {output_path}'
                ffmpeg_result = os.system(ffmpeg_cmd)
                if ffmpeg_result != 0:
                    raise Exception(
                        f"FFmpeg command failed with exit code {ffmpeg_result}")

                # Read final video
                with open(output_path, 'rb') as f:
                    video_data = f.read()

                return video_data

        except Exception as e:
            raise Exception(f"Error generating video: {str(e)}")

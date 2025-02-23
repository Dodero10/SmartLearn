from typing import Any, Dict

from constants.constants import (BUCKET_NAME_AUDIO, BUCKET_NAME_METADATA,
                                 BUCKET_NAME_SCRIPTS, BUCKET_NAME_VIDEO)
from utils.minio_utils import save_file_to_minio

from .audio_generator import AudioGenerator
from .script_generator import ScriptGenerator
from .slide_processor import SlideProcessor
from .video_generator import VideoGenerator


class LectureGenerator:
    def __init__(self, file_data: bytes, filename: str):
        self.file_data = file_data
        self.filename = filename
        self.base_filename = f"{filename.replace('.pdf', '')}"

    def _save_to_minio(self, data: bytes | str, suffix: str, bucket: str, content_type: str) -> str:
        """Helper method to save files to MinIO"""
        if isinstance(data, str):
            data = data.encode()

        # For scripts, create a folder structure
        if bucket == BUCKET_NAME_SCRIPTS:
            folder_name = self.base_filename
            if suffix.startswith("/"):
                output_filename = f"{folder_name}{suffix}"
            else:
                output_filename = f"{folder_name}/{suffix}"
        else:
            output_filename = f"{self.base_filename}{suffix}"

        save_file_to_minio(
            file_data=data,
            filename=output_filename,
            bucket_name=bucket,
            content_type=content_type
        )
        return output_filename

    def generate(self) -> Dict[str, Any]:
        """Generate complete lecture materials from PDF"""
        try:
            # 1. Process slides and extract metadata
            processor = SlideProcessor(self.file_data, self.filename)
            lecture_metadata = processor.process_slides()
            # Use the same folder name as slides for file names
            self.base_filename = processor.folder_name

            # 2. Save metadata
            metadata_filename = self._save_to_minio(
                lecture_metadata.json(),
                ".json",
                BUCKET_NAME_METADATA,
                "application/json"
            )

            # 3. Generate and save script
            script_generator = ScriptGenerator(lecture_metadata)
            full_script, slide_scripts = script_generator.generate_script()

            print(full_script)  # Phúc lấy ở đây

            # Save main script with just the base name
            script_filename = self._save_to_minio(
                full_script,
                f"/{self.base_filename}.txt",
                BUCKET_NAME_SCRIPTS,
                "text/plain"
            )

            # Save individual slide scripts in the same folder
            slide_script_filenames = []
            for i, script in enumerate(slide_scripts, 1):
                filename = self._save_to_minio(
                    script,
                    f"slide_{i}_script.txt",
                    BUCKET_NAME_SCRIPTS,
                    "text/plain"
                )
                slide_script_filenames.append(filename)

            # 4. Generate and save audio for each slide
            audio_generator = AudioGenerator(lecture_metadata)
            audio_files = audio_generator.generate_audio()
            audio_filenames = []

            for audio_filename, audio_data in audio_files:
                full_filename = self._save_to_minio(
                    audio_data,
                    f"/{audio_filename}",
                    BUCKET_NAME_AUDIO,
                    "audio/mpeg"
                )
                audio_filenames.append(full_filename)

            # 5. Generate and save video
            video_generator = VideoGenerator(
                lecture_metadata, self.file_data, audio_files)
            video_data = video_generator.generate_video()
            video_filename = self._save_to_minio(
                video_data,
                ".mp4",
                BUCKET_NAME_VIDEO,
                "video/mp4"
            )

            return {
                "status": "success",
                "message": "Lecture generation completed successfully",
                "metadata_file": metadata_filename,
                "script_file": script_filename,
                "slide_scripts": slide_script_filenames,
                "audio_files": audio_filenames,
                "video_file": video_filename
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Error generating lecture: {str(e)}"
            }

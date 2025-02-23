import io
import json
import os
from typing import List, Tuple

from google.cloud import texttospeech
from google.oauth2 import service_account

from .models import LectureMetadata


class AudioGenerator:
    def __init__(self, lecture_metadata: LectureMetadata):
        self.lecture_metadata = lecture_metadata
        self.client = self._create_client()

    def _create_client(self):
        """Create Text-to-Speech client with credentials"""
        try:
            # Try to get credentials from environment variable
            credentials_json = os.getenv('GOOGLE_CREDENTIALS')
            if credentials_json:
                # Parse credentials from JSON string
                credentials_info = json.loads(credentials_json)
                credentials = service_account.Credentials.from_service_account_info(
                    credentials_info)
                return texttospeech.TextToSpeechClient(credentials=credentials)
            else:
                # Try to get credentials from file
                credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
                if credentials_path and os.path.exists(credentials_path):
                    return texttospeech.TextToSpeechClient()
                else:
                    raise ValueError("Google Cloud credentials not found")
        except Exception as e:
            raise ValueError(f"Error creating Text-to-Speech client: {str(e)}")

    def _generate_single_audio(self, text: str) -> bytes:
        """Generate audio for a single piece of text"""
        # Configure the synthesis input
        synthesis_input = texttospeech.SynthesisInput(text=text)

        # Build the voice request with Vietnamese voice
        voice = texttospeech.VoiceSelectionParams(
            language_code="vi-VN",
            name="vi-VN-Neural2-A",  # High quality Vietnamese female voice
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
        )

        # Select the audio file type with teacher-like characteristics
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=0.9,  # Slightly slower for clarity
            pitch=0.5,  # Slightly higher pitch for authority
            volume_gain_db=2.0,  # Slightly louder
            effects_profile_id=["telephony-class-application"]
        )

        # Perform the text-to-speech request
        response = self.client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )

        return response.audio_content

    def generate_audio(self) -> List[Tuple[str, bytes]]:
        """Generate audio files for each slide"""
        if not self.lecture_metadata.script:
            raise ValueError("No script available in lecture metadata")

        # Split script into slides based on the "---" delimiter
        slide_scripts = self.lecture_metadata.script.split("---")

        audio_files = []

        # Generate audio for each slide
        for i, script in enumerate(slide_scripts, 1):
            if script.strip():  # Only process non-empty scripts
                try:
                    audio_content = self._generate_single_audio(script.strip())
                    filename = f"slide{i}.mp3"
                    audio_files.append((filename, audio_content))
                except Exception as e:
                    print(f"Error generating audio for slide {i}: {str(e)}")
                    continue

        return audio_files

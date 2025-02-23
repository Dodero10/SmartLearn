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
        slide_scripts = []  # Store individual slide scripts

        for idx, slide in enumerate(self.lecture_metadata.slides):
            # Construct the prompt for the OpenAI model
            prompt = f"Please generate a script for slide {slide.slide_number}. Title: {slide.title}. " \
                f"Content: {slide.text_content}. " \
                f"Image description: {', '.join([image.description for image in slide.images if image.description])}. " \
                f"Provide a brief explanation and connect it to the previous slide if applicable."

            # Call OpenAI API to generate script for the slide
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates lecture scripts from slide metadata."},
                    {"role": "user", "content": prompt}
                ]
            )

            slide_script = response.choices[0].message.content.strip()

            # Store the individual slide script
            slide_scripts.append(slide_script)

            # Add slide title and generated script to the full script
            script_parts.append(f"Slide {slide.slide_number}: {slide.title}\n")
            script_parts.append(slide_script)

            # If there is a next slide, add a connection to the next slide
            if idx + 1 < len(self.lecture_metadata.slides):
                next_slide = self.lecture_metadata.slides[idx + 1]
                transition = f"Next, we will move on to slide {next_slide.slide_number} which covers {next_slide.title}.\n"
                script_parts.append(transition)
                # Add transition to the current slide's script
                slide_scripts[-1] = slide_scripts[-1] + "\n" + transition

            script_parts.append("\n---\n")

        # Join all parts with proper spacing
        full_script = "\n".join(script_parts)

        # Update lecture metadata with the generated script
        self.lecture_metadata.script = full_script

        return full_script, slide_scripts

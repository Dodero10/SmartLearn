from .models import LectureMetadata


class ScriptGenerator:
    def __init__(self, lecture_metadata: LectureMetadata):
        self.lecture_metadata = lecture_metadata
        
    def generate_script(self) -> str:
        """Generate a lecture script from slide metadata"""
        script_parts = []
        
        for slide in self.lecture_metadata.slides:
            # Add slide title
            script_parts.append(f"Slide {slide.slide_number}: {slide.title}\n")
            
            # Add slide content
            script_parts.append(slide.text_content)
            
            # Add image descriptions
            for image in slide.images:
                if image.description:
                    script_parts.append(f"In this slide, we can see {image.description}")
            
            # Add table descriptions
            for table in slide.tables:
                script_parts.append("Let's look at the following table data:")
                for row in table.rows:
                    script_parts.append(" | ".join(row))
            
            script_parts.append("\n---\n")
        
        # Join all parts with proper spacing
        full_script = "\n".join(script_parts)
        
        # Update lecture metadata with the generated script
        self.lecture_metadata.script = full_script
        
        return full_script 
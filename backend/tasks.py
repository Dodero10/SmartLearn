import io
import os

from chat_query.query import query
from config.celery_app import celery_app
from config.minio_client import bucket_name, bucket_name_slide, minio_client
from fastapi.responses import StreamingResponse
from file_processing.file_processing import chunking, parsing
from gen_lecture.audio_generator import AudioGenerator
from gen_lecture.script_generator import ScriptGenerator
from gen_lecture.slide_processor import SlideProcessor
from PIL import Image
from utils.database_manage import DatabaseManager
from utils.minio_utils import save_file_to_minio


@celery_app.task(name='tasks.save_pdf_to_minio')
def save_pdf_to_minio(file_data: bytes, filename: str):
    try:
        file_stream = io.BytesIO(file_data)
        content = parsing(file_stream, filename)
        data, metadata, ids = chunking(content, filename=filename)

        try:
            minio_client.stat_object(bucket_name, filename)
            return f"File {filename} đã tồn tại trong MinIO."
        except Exception as e:
            if "NoSuchKey" in str(e):
                pass
            else:
                return f"Error checking file existence: {str(e)}"

        databaseManager = DatabaseManager()
        databaseManager.add_data(data, metadata, ids)
        minio_client.put_object(
            bucket_name=bucket_name,
            object_name=filename,
            data=file_stream,
            length=len(file_data),
            content_type='application/pdf'
        )

        return {"message": f"Tạo thư mục {filename.replace('.pdf', '')} và lưu cơ sở dữ liệu thành công."}

    except Exception as e:
        return f"Error uploading file {filename}: {str(e)}"


@celery_app.task(name='tasks.download_pdf_from_minio')
def download_pdf_from_minio(filename: str):
    try:
        response = minio_client.get_object(bucket_name, filename)

        file_stream = io.BytesIO(response.read())
        file_stream.seek(0)
        return file_stream.getvalue()

    except Exception as e:
        return str(e)


@celery_app.task(name='tasks.delete_pdf')
def delete_pdf_and_images(filename: str):
    try:
        minio_client.remove_object(bucket_name, filename)

        databaseManager = DatabaseManager()
        databaseManager.delete_data(filename=filename)

        return f"File {filename} và các ảnh liên quan đã được xóa thành công."

    except Exception as e:
        return str(e)
    

##### Dat
@celery_app.task(name='tasks.upload_slide')
def upload_slide(file_data: bytes, filename: str):
    try:
        result = save_file_to_minio(
            file_data=file_data,
            filename=filename,
            bucket_name=bucket_name_slide,
            content_type='application/pdf'
        )
        return result
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error uploading slide: {str(e)}"
        }

##### Dat

@celery_app.task(name='tasks.generate_lecture')
def generate_lecture(file_data: bytes, filename: str):
    try:
        # 1. Process slides and extract metadata
        processor = SlideProcessor(file_data, filename)
        lecture_metadata = processor.process_slides()
        
        # 2. Save metadata to MinIO
        metadata_json = lecture_metadata.json()
        metadata_filename = f"{filename.replace('.pdf', '')}_metadata.json"
        save_file_to_minio(
            file_data=metadata_json.encode(),
            filename=metadata_filename,
            bucket_name="metadata",
            content_type="application/json"
        )
        
        # 3. Generate script
        script_generator = ScriptGenerator(lecture_metadata)
        script = script_generator.generate_script()
        
        # 4. Save script to MinIO
        script_filename = f"{filename.replace('.pdf', '')}_script.txt"
        save_file_to_minio(
            file_data=script.encode(),
            filename=script_filename,
            bucket_name="scripts",
            content_type="text/plain"
        )
        
        # 5. Generate audio
        audio_generator = AudioGenerator(lecture_metadata)
        audio_data = audio_generator.generate_audio()
        
        # 6. Save audio to MinIO
        audio_filename = f"{filename.replace('.pdf', '')}.mp3"
        save_file_to_minio(
            file_data=audio_data,
            filename=audio_filename,
            bucket_name="audio",
            content_type="audio/mpeg"
        )
        
        return {
            "status": "success",
            "message": "Lecture generation completed successfully",
            "metadata_file": metadata_filename,
            "script_file": script_filename,
            "audio_file": audio_filename
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error generating lecture: {str(e)}"
        }

##### Dat

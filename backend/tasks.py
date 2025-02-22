import io
import os

from chat_query.query import query
from config.celery_app import celery_app
from config.minio_client import bucket_name, bucket_name_slide, minio_client
from constants.constants import (BUCKET_NAME, BUCKET_NAME_AUDIO,
                                 BUCKET_NAME_METADATA, BUCKET_NAME_SCRIPTS,
                                 BUCKET_NAME_SLIDE, BUCKET_NAME_VIDEO)
from fastapi.responses import StreamingResponse
from file_processing.file_processing import chunking, parsing
from gen_lecture.audio_generator import AudioGenerator
from gen_lecture.lecture_generator import LectureGenerator
from gen_lecture.script_generator import ScriptGenerator
from gen_lecture.slide_processor import SlideProcessor
from gen_lecture.video_generator import VideoGenerator
from generaldb.service import DatabaseService
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


# Dat
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

# Dat


@celery_app.task(name='tasks.generate_lecture')
def generate_lecture(file_data: bytes, filename: str):
    try:
        generator = LectureGenerator(file_data, filename)
        return generator.generate()
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error generating lecture: {str(e)}"
        }

# Dat


@celery_app.task(name='tasks.get_history')
def get_history_task(user_id: str):
    try:
        result = DatabaseService.get_history(user_id)
        return result
    except Exception as e:
        return {"error": str(e)}


@celery_app.task(name='tasks.get_setting')
def get_setting_task(user_id: str, key: str):
    try:
        result = DatabaseService.get_setting(user_id, key)
        return result
    except Exception as e:
        return {"error": str(e)}


@celery_app.task(name='tasks.create_project')
def create_project_task(user_id: str, project_name: str):
    try:
        result = DatabaseService.create_project(user_id, project_name)
        return result
    except Exception as e:
        return {"error": str(e)}


@celery_app.task(name='tasks.create_chat')
def create_chat_task(project_id: str, title: str):
    try:
        result = DatabaseService.create_chat(project_id, title)
        return result
    except Exception as e:
        return {"error": str(e)}


@celery_app.task(name='tasks.upload_file_db')
def upload_file_db_task(chat_id: str, file_name: str, file_type: str, size: int):
    try:
        result = DatabaseService.upload_file(
            chat_id, file_name, file_type, size)
        return result
    except Exception as e:
        return {"error": str(e)}


@celery_app.task(name='tasks.send_message')
def send_message_task(chat_id: str, role: str, content: str):
    try:
        result = DatabaseService.send_message(chat_id, role, content)
        return result
    except Exception as e:
        return {"error": str(e)}


@celery_app.task(name='tasks.push_setting')
def push_setting_task(user_id: str, key: str, value: str):
    try:
        result = DatabaseService.push_setting(user_id, key, value)
        return result
    except Exception as e:
        return {"error": str(e)}


@celery_app.task(name='tasks.delete_chat')
def delete_chat_task(chat_id: str):
    try:
        DatabaseService.delete_chat(chat_id)
        return True
    except Exception as e:
        return {"error": str(e)}


@celery_app.task(name='tasks.get_chat_message')
def get_chat_message_task(chat_id: str):
    try:
        result = DatabaseService.get_chat_messages(chat_id)
        return result
    except Exception as e:
        return {"error": str(e)}


@celery_app.task(name='tasks.delete_file_in_chat')
def delete_file_in_chat_task(chat_id: str):
    try:
        DatabaseService.delete_file_in_chat(chat_id)
        return True
    except Exception as e:
        return {"error": str(e)}


@celery_app.task(name='tasks.update_name_project')
def update_name_project_task(project_id: str, new_name: str):
    try:
        DatabaseService.update_name_project(project_id, new_name)
        return True
    except Exception as e:
        return {"error": str(e)}


@celery_app.task(name='tasks.update_name_chat')
def update_name_chat_task(chat_id: str, new_name: str):
    try:
        DatabaseService.update_name_chat(chat_id, new_name)
        return True
    except Exception as e:
        return {"error": str(e)}


@celery_app.task(name='tasks.search_chat')
def search_chat_task(user_id: str, keyword: str):
    try:
        result = DatabaseService.search_chat(user_id, keyword)
        return result
    except Exception as e:
        return {"error": str(e)}

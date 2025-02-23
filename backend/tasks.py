import io
import os

from chat_query.query import query
from config.celery_app import celery_app
from config.minio_client import bucket_name, bucket_name_slide, minio_client
from constants.constants import (BUCKET_NAME, BUCKET_NAME_AUDIO,
                                 BUCKET_NAME_METADATA, BUCKET_NAME_SCRIPTS,
                                 BUCKET_NAME_SLIDE, BUCKET_NAME_VIDEO)
from fastapi import HTTPException, status
from file_processing.file_processing import chunking, parsing
from gen_lecture.e2e_lecture import LectureGenerator
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


@celery_app.task(name='tasks.generate_lecture')
def generate_lecture(file_data: bytes, filename: str):
    try:
        # Check if folder already exists
        folder_name = filename.replace('.pdf', '')
        try:
            # List objects in the bucket with the folder prefix
            objects = minio_client.list_objects(
                bucket_name_slide, prefix=f"{folder_name}/")
            # If there are any objects with this prefix, the folder exists
            if any(obj.object_name.startswith(f"{folder_name}/") for obj in objects):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"File '{filename}' đã tồn tại trong hệ thống"
                )
        except HTTPException as e:
            return {
                "status": "error",
                "status_code": e.status_code,
                "message": e.detail
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error checking folder existence: {str(e)}"
            }

        generator = LectureGenerator(file_data, filename)
        return generator.generate()
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error generating lecture: {str(e)}"
        }


@celery_app.task(name='tasks.download_video_from_minio')
def download_video_from_minio(filename: str):
    try:
        response = minio_client.get_object(BUCKET_NAME_VIDEO, filename)

        file_stream = io.BytesIO(response.read())
        file_stream.seek(0)
        return file_stream.getvalue()

    except Exception as e:
        return str(e)

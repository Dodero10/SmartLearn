import io
from minio_client import minio_client, bucket_name
from celery_app import celery_app
import os
from pdf2image import convert_from_bytes
from PIL import Image
from fastapi.responses import StreamingResponse
from file_processing.file_processing import parsing,chunking
from utils.database_manage import DatabaseManager
from chat_query.query import query
@celery_app.task(name='tasks.save_pdf_to_minio')
def save_pdf_to_minio(file_data: bytes, filename: str):
    try:
        file_stream = io.BytesIO(file_data)
        content= parsing(file_stream, filename)
        data, metadata, ids= chunking(content,filename=filename)
        

        try:
            minio_client.stat_object(bucket_name, filename)
            return f"File {filename} đã tồn tại trong MinIO."
        except Exception as e:
            if "NoSuchKey" in str(e):
                pass  
            else:
                return f"Error checking file existence: {str(e)}"

        databaseManager=DatabaseManager()
        databaseManager.add_data(data,metadata,ids)
        minio_client.put_object(
            bucket_name=bucket_name,
            object_name=filename, 
            data=file_stream,
            length=len(file_data),
            content_type='application/pdf'
        )

        
        return { "message": f"Tạo thư mục {filename.replace('.pdf', '')} và lưu cơ sở dữ liệu thành công."}

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
        
        databaseManager=DatabaseManager()
        databaseManager.delete_data(filename=filename)

        return f"File {filename} và các ảnh liên quan đã được xóa thành công."

    except Exception as e:
        return str(e)

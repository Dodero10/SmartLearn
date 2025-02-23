import io
from typing import Union

from config.minio_client import minio_client


def save_file_to_minio(
    file_data: Union[bytes, io.BytesIO],
    filename: str,
    bucket_name: str,
    content_type: str = None
) -> dict:
    """
    Save a file to MinIO with specified parameters.
    
    Args:
        file_data: The file data as bytes or BytesIO object
        filename: Name of the file to be saved
        bucket_name: Name of the bucket to save the file in
        content_type: MIME type of the file (optional)
    
    Returns:
        dict: A dictionary containing the status of the operation
    """
    try:
        # Convert to BytesIO if input is bytes
        if isinstance(file_data, bytes):
            file_stream = io.BytesIO(file_data)
        else:
            file_stream = file_data
            
        # Get file size
        file_stream.seek(0, 2)  # Seek to end
        file_size = file_stream.tell()
        file_stream.seek(0)  # Reset to beginning
        
        # Check if bucket exists, create if it doesn't
        try:
            minio_client.stat_object(bucket_name, filename)
            return {
                "status": "error",
                "message": f"File {filename} already exists in bucket {bucket_name}"
            }
        except Exception as e:
            if "NoSuchKey" in str(e):
                pass  # File doesn't exist, we can proceed
            elif "NoSuchBucket" in str(e):
                # Create bucket if it doesn't exist
                minio_client.make_bucket(bucket_name)
            else:
                raise e

        # Upload file to MinIO
        minio_client.put_object(
            bucket_name=bucket_name,
            object_name=filename,
            data=file_stream,
            length=file_size,
            content_type=content_type
        )

        return {
            "status": "success",
            "message": f"File {filename} uploaded successfully to bucket {bucket_name}",
            "bucket": bucket_name,
            "filename": filename
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error uploading file: {str(e)}"
        } 
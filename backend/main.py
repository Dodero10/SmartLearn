import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from celery.result import AsyncResult
from minio_client import minio_client,bucket_name
from celery_app import celery_app
from celery import chain
from fastapi.responses import StreamingResponse
import io
from tasks import save_pdf_to_minio, delete_pdf_and_images,download_pdf_from_minio
import asyncio
app = FastAPI()


@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        return {"error": "Chỉ chấp nhận file PDF"}

   
    file_data = await file.read()

   
    filename = file.filename

    task = save_pdf_to_minio.delay(file_data, filename)

    return {"task_id": task.id, "message": "File đang được tải lên"}

@app.get("/task_status/{task_id}")
def get_task_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)
    
    if task_result.state == "PENDING":
        return {"status": "Đang chờ xử lý"}
    elif task_result.state == "SUCCESS":
        return {"status": "Thành công", "result": task_result.result}
    elif task_result.state == "FAILURE":
        return {"status": "Thất bại"}
    else:
        return {"status": task_result.state}



@app.get("/download/{filename}")
async def download_file(filename: str):
    task = celery_app.send_task('tasks.download_pdf_from_minio', args=[filename])
    while True:
        result = AsyncResult(task.id, app=celery_app)
        
        if result.state == "SUCCESS":
            file_data = result.result
            if isinstance(file_data, bytes):
                return StreamingResponse(
                    io.BytesIO(file_data),
                    media_type='application/pdf',
                    headers={"Content-Disposition": f"attachment; filename={filename}"}
                )
            else:
                raise HTTPException(status_code=500, detail="File không đúng định dạng.")
        
        elif result.state == "FAILURE":
            raise HTTPException(status_code=500, detail="Tải xuống thất bại.")
        
        elif result.state == "PENDING":
            await asyncio.sleep(1)
        
        else:
            raise HTTPException(status_code=500, detail="Lỗi không xác định.")
    
@app.get("/list_pdfs")
async def list_pdfs():
    try:
        objects = minio_client.list_objects(bucket_name, recursive=True)
        pdf_files = [obj.object_name for obj in objects if obj.object_name.endswith('.pdf')]
        
        return {"pdf_files": pdf_files}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
@app.delete("/delete_pdf/{filename}")
async def delete_pdf(filename: str):
    task = celery_app.send_task('tasks.delete_pdf', args=[filename])
    
    while True:
        result = AsyncResult(task.id, app=celery_app)
        
        if result.state == "SUCCESS":
            response_message = result.result
            if isinstance(response_message, str):
                return {"message": response_message}
            else:
                raise HTTPException(status_code=500, detail="Xóa thất bại.")
        
        elif result.state == "FAILURE":
            response_message = result.result
            raise HTTPException(status_code=500, detail=f"Xóa thất bại: {response_message}")
        
        elif result.state == "PENDING":
            await asyncio.sleep(1)
        
        else:
            raise HTTPException(status_code=500, detail="Lỗi không xác định")
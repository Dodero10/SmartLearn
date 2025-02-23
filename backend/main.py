import asyncio
import io
import logging
import os
from datetime import datetime

from celery import chain
from celery.result import AsyncResult
from chat_query.query import gen_quiz, query
from config.celery_app import celery_app
from config.minio_client import bucket_name, bucket_name_video, minio_client
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from tasks import generate_lecture, save_pdf_to_minio, upload_slide

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Định nghĩa model cho request body


class TutorQuery(BaseModel):
    question: str


app = FastAPI(
    title="Chat API",
    description="API for chat application",
    version="1.0.0"
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


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
    task = celery_app.send_task(
        'tasks.download_pdf_from_minio', args=[filename])
    while True:
        result = AsyncResult(task.id, app=celery_app)

        if result.state == "SUCCESS":
            file_data = result.result
            if isinstance(file_data, bytes):
                return StreamingResponse(
                    io.BytesIO(file_data),
                    media_type='application/pdf',
                    headers={
                        "Content-Disposition": f"attachment; filename={filename}"}
                )
            else:
                raise HTTPException(
                    status_code=500, detail="File không đúng định dạng.")

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
        pdf_files = [
            obj.object_name for obj in objects if obj.object_name.endswith('.pdf')]

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
            raise HTTPException(
                status_code=500, detail=f"Xóa thất bại: {response_message}")

        elif result.state == "PENDING":
            await asyncio.sleep(1)

        else:
            raise HTTPException(status_code=500, detail="Lỗi không xác định")

@app.post("/ai_tutor_query")
async def ai_tutor_query(query_data: TutorQuery):
    try:
        def stream_answer():
            try:
                for chunk in query(question=query_data.question):
                    yield f"data: {chunk}\n\n"
            except Exception as e:
                yield f"data: Lỗi server, vui lòng thử lại sau!\n\n"

        return StreamingResponse(
            stream_answer(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
                "Access-Control-Allow-Origin": "http://localhost:3000",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Credentials": "true",
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/gen_quizz")
def gen_quizz(filenames:list[str]):
    try:
        quizzes=gen_quiz(filenames=filenames)
        return quizzes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    
@app.get("/test")
def test():
    data=DatabaseManager()
    return data.collection.get()


####### Dat

@app.post("/upload_slide", tags=["Slide2Video"])

async def handle_upload_slide(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        return {"error": "Chỉ chấp nhận file PDF"}

    file_data = await file.read()

    filename = file.filename

    task = upload_slide.delay(file_data, filename)
    
    return {"task_id": task.id, "message": "File đang được tải lên"}
    



@app.post("/generate_lecture", tags=["Slide2Video"])
async def handle_generate_lecture(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        return {"error": "Chỉ chấp nhận file PDF"}

    file_data = await file.read()
    filename = file.filename

    task = generate_lecture.delay(file_data, filename)
    return {"task_id": task.id, "message": "Đang xử lý lecture"}

@app.get("/download_video/{filename}", tags=["Slide2Video"])
async def download_file(filename: str):
    task = celery_app.send_task(
        'tasks.download_video_from_minio', args=[filename])
    while True:
        result = AsyncResult(task.id, app=celery_app)

        if result.state == "SUCCESS":
            file_data = result.result
            if isinstance(file_data, bytes):
                return StreamingResponse(
                    io.BytesIO(file_data),
                    media_type='video/mp4',
                    headers={
                        "Content-Disposition": f"attachment; filename={filename}"}
                )
            else:
                raise HTTPException(
                    status_code=500, detail="File không đúng định dạng.")

        elif result.state == "FAILURE":
            raise HTTPException(status_code=500, detail="Tải xuống thất bại.")

        elif result.state == "PENDING":
            await asyncio.sleep(1)

        else:
            raise HTTPException(status_code=500, detail="Lỗi không xác định.")
        
@app.get("/list_videos", tags=["Slide2Video"])
async def list_videos():
    try:
        objects = minio_client.list_objects(bucket_name_video, recursive=True)
        videos = [
            obj.object_name for obj in objects if obj.object_name.endswith('.mp4')]

        return {"videos": videos}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


####### Dat
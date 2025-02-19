import asyncio
import io
import logging
import os
from datetime import datetime
from utils.database_manage import DatabaseManager
from celery import chain
from celery.result import AsyncResult
from chat_query.query import gen_quiz, query
from config.celery_app import celery_app
from config.minio_client import bucket_name, minio_client
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from generaldb.models import User
from passlib.hash import bcrypt
from pydantic import BaseModel, EmailStr, Field
from tasks import (create_chat_task, delete_chat_task,
                   delete_file_in_chat_task, delete_pdf_and_images,
                   download_pdf_from_minio, generate_lecture,
                   get_chat_message_task, get_history_task, get_setting_task,
                   push_setting_task, save_pdf_to_minio, search_chat_task,
                   send_message_task, update_name_chat_task, upload_file_db_task, upload_slide,
                   get_user_files_task, delete_file_task, toggle_file_selection_task)

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


@app.options("/ai_tutor_query")
async def ai_tutor_query_options():
    return {"message": "OK"}

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

@app.post("/upload_slide")
async def handle_upload_slide(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        return {"error": "Chỉ chấp nhận file PDF"}

    file_data = await file.read()

    filename = file.filename

    task = upload_slide.delay(file_data, filename)
    
    return {"task_id": task.id, "message": "File đang được tải lên"}
    



@app.post("/generate_lecture")
async def handle_generate_lecture(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        return {"error": "Chỉ chấp nhận file PDF"}

    file_data = await file.read()
    filename = file.filename

    task = generate_lecture.delay(file_data, filename)
    return {"task_id": task.id, "message": "Đang xử lý lecture"}


####### Dat
####### Phuc

class ChatCreate(BaseModel):
    user_id: str = Field(..., description="ID của user") 
    title: str = Field(..., description="Tiêu đề chat")

class MessageCreate(BaseModel):
    chat_id: str = Field(..., description="ID của chat")
    role: str = Field(..., description="Vai trò (user/bot)")
    content: str = Field(..., description="Nội dung tin nhắn")

class SettingCreate(BaseModel):
    user_id: str = Field(..., description="ID của user")
    key: str = Field(..., description="Khóa setting")
    value: str = Field(..., description="Giá trị setting")

@app.get("/history/{user_id}", 
    tags=["Chat"],
    summary="Lấy lịch sử chat",
    response_description="Danh sách các chat"
)
async def get_chat_history(user_id: str):
    task = get_history_task.delay(user_id)
    result = await handle_task_result(task)
    return result

@app.get("/setting/{user_id}/{key}")
async def get_user_setting(user_id: str, key: str):
    task = get_setting_task.delay(user_id, key)
    result = await handle_task_result(task)
    return result

@app.post("/chat")
async def create_new_chat(chat: ChatCreate):
    task = create_chat_task.delay(chat.user_id, chat.title)
    result = await handle_task_result(task)
    return result

@app.post("/message")
async def send_new_message(message: MessageCreate):
    task = send_message_task.delay(message.chat_id, message.role, message.content)
    result = await handle_task_result(task)
    return result

@app.post("/setting")
async def create_setting(setting: SettingCreate):
    task = push_setting_task.delay(setting.user_id, setting.key, setting.value)
    result = await handle_task_result(task)
    return result

@app.delete("/chat/{chat_id}")
async def remove_chat(chat_id: str):
    task = delete_chat_task.delay(chat_id)
    result = await handle_task_result(task)
    return result

@app.get("/chat/{chat_id}/messages")
async def get_messages(chat_id: str):
    task = get_chat_message_task.delay(chat_id)
    result = await handle_task_result(task)
    return result

@app.delete("/chat/{chat_id}/files")
async def delete_chat_files(chat_id: str):
    task = delete_file_in_chat_task.delay(chat_id)
    result = await handle_task_result(task)
    return result

@app.get("/search/{user_id}")
async def search_chats(user_id: str, keyword: str):
    task = search_chat_task.delay(user_id, keyword)
    result = await handle_task_result(task)
    return result

# Helper function để xử lý kết quả task
async def handle_task_result(task):
    while True:
        result = AsyncResult(task.id, app=celery_app)
        if result.ready():
            if result.successful():
                return result.result
            else:
                raise HTTPException(status_code=500, detail="Task failed")
        await asyncio.sleep(0.1)

# User Pydantic models
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserResponse(BaseModel):
    user_id: int
    username: str
    email: str
    created_at: datetime

@app.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate):
    try:
        # Generate a new user_id
        last_user = User.objects.order_by('-user_id').first()
        new_user_id = 1 if not last_user else last_user.user_id + 1
        
        # Hash the password
        hashed_password = bcrypt.hash(user.password)
        
        # Create new user
        db_user = User(
            user_id=new_user_id,
            username=user.username,
            email=user.email,
            password_hash=hashed_password
        )
        db_user.save()
        
        return {
            "user_id": db_user.user_id,
            "username": db_user.username,
            "email": db_user.email,
            "created_at": db_user.created_at
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/users/", response_model=list[UserResponse])
async def get_users():
    try:
        users = User.objects.all()
        return [{
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at
        } for user in users]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    try:
        user = User.objects.get(user_id=user_id)
        return {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at
        }
    except User.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/files/upload")
async def upload_file_to_db(
    user_id: str,
    file_name: str,
    file_type: str
):
    task = upload_file_db_task.delay(user_id, file_name, file_type)
    result = await handle_task_result(task)
    return result

@app.get("/files/{user_id}")
async def get_user_files(user_id: str):
    task = get_user_files_task.delay(user_id)
    result = await handle_task_result(task)
    return result

@app.delete("/files/{file_id}")
async def delete_file(file_id: str):
    task = delete_file_task.delay(file_id)
    result = await handle_task_result(task)
    return result

@app.put("/files/{file_id}/toggle")
async def toggle_file_selection(file_id: str):
    task = toggle_file_selection_task.delay(file_id)
    result = await handle_task_result(task)
    return result

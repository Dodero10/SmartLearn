import asyncio
import io
import os
from datetime import datetime

from celery import chain
from celery.result import AsyncResult
from chat_query.query import gen_quiz, query
from config.celery_app import celery_app
from config.minio_client import bucket_name, minio_client
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from generaldb.models import User
from passlib.hash import bcrypt
from pydantic import BaseModel, EmailStr, Field
from tasks import (create_chat_task, create_project_task, delete_chat_task,
                   delete_file_in_chat_task, delete_pdf_and_images,
                   download_pdf_from_minio, generate_lecture,
                   get_chat_message_task, get_history_task, get_setting_task,
                   push_setting_task, save_pdf_to_minio, search_chat_task,
                   send_message_task, update_name_chat_task,
                   update_name_project_task, upload_file_db_task, upload_slide)

app = FastAPI(
    title="Chat API",
    description="API for chat application",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
async def ai_tutor_query(question: str):
    try:
        async def stream_response():
            try:
                # Convert sync generator to async
                for chunk in query(question=question):
                    yield chunk
                    # Add a small delay to prevent blocking
                    await asyncio.sleep(0.01)
            except Exception as e:
                error_msg = f"Error during query processing: {str(e)}"
                print(error_msg)  # Log the error
                yield f"Lỗi server: {error_msg}"

        return StreamingResponse(
            stream_response(),
            media_type="text/plain"
        )
    except Exception as e:
        error_msg = f"Error in endpoint: {str(e)}"
        print(error_msg)  # Log the error
        raise HTTPException(status_code=500, detail=error_msg)


@app.post("/gen_quizz")
def gen_quizz(filenames: list[str]):
    try:
        quizzes = gen_quiz(filenames=filenames)
        return quizzes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


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

class ProjectCreate(BaseModel):
    user_id: str = Field(..., description="ID của user")
    project_name: str = Field(..., description="Tên project")

class ChatCreate(BaseModel):
    project_id: str = Field(..., description="ID của project") 
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

@app.post("/project",
    tags=["Project"], 
    summary="Tạo project mới",
    response_description="Project đã được tạo"
)
async def create_new_project(project: ProjectCreate):
    task = create_project_task.delay(project.user_id, project.project_name)
    result = await handle_task_result(task)
    return result

@app.post("/chat")
async def create_new_chat(chat: ChatCreate):
    task = create_chat_task.delay(chat.project_id, chat.title)
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

@app.put("/project/{project_id}/name/{new_name}")
async def rename_project(project_id: str, new_name: str):
    task = update_name_project_task.delay(project_id, new_name)
    result = await handle_task_result(task)
    return result

@app.put("/chat/{chat_id}/name/{new_name}")
async def rename_chat(chat_id: str, new_name: str):
    task = update_name_chat_task.delay(chat_id, new_name)
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

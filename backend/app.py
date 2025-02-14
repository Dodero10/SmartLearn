import openai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
import os

# Tải các biến môi trường từ file .env
load_dotenv()

# Cấu hình API Key của OpenAI từ biến môi trường
openai.api_key = os.getenv('OPENAI_API_KEY')

app = FastAPI()

# Định nghĩa các model cho request và response
class ChatRequest(BaseModel):
    question: str
    thread_id: str

class ChatResponse(BaseModel):
    answer: str

class ChatStreamRequest(BaseModel):
    question: str
    thread_id: str
    model: str

@app.post("/api/v1/chat/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Lấy dữ liệu từ request (tin nhắn và session_id)
        message = request.question
        thread_id = request.thread_id

        # Gửi request đến API của OpenAI để lấy phản hồi từ ChatGPT
        response = openai.Completion.create(
            engine="text-davinci-003",  # Có thể thay đổi thành model khác như GPT-4 nếu cần
            prompt=message,
            max_tokens=150,
            temperature=0.7
        )

        # Trả về kết quả
        return ChatResponse(answer=response.choices[0].text.strip())

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/chat/chat/stream")
async def chat_stream(request: ChatStreamRequest):
    try:
        # Lấy dữ liệu từ request
        message = request.question
        thread_id = request.thread_id
        model = request.model

        # Gửi request đến API của OpenAI để nhận phản hồi dạng stream
        response = openai.Completion.create(
            engine=model,
            prompt=message,
            max_tokens=150,
            temperature=0.7,
            stream=True
        )

        # Trả về từng chunk dữ liệu trong stream
        def generate():
            for chunk in response:
                if chunk.get('choices'):
                    yield f"data: {chunk['choices'][0]['text']}\n\n"

        return EventSourceResponse(generate())

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Chạy ứng dụng FastAPI với Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8030)

FROM python:3.10-slim

# Cài đặt các gói cần thiết
RUN apt update && apt-get install -y ffmpeg poppler-utils &&\
    apt clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
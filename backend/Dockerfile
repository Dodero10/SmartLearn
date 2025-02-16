FROM python:3.10-slim

# Install system dependencies and clean up in a single layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    poppler-utils \
    ffmpeg \
    gcc \
    python3-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
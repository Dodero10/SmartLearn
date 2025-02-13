# Automation-Chatbot

## Setup

1. Run Frontend:

- Step 1: Tạo file .env từ file .env.example: `cp .env.example .env`
- Step 2: CD vào folder chatbot-frontend: `cd chatbot-frontend`
- Step 3: Install dependencies: `npm install`
- Step 4: Run frontend: `npm start`

2. Run Backend:

- Step 1: Tạo file .env từ file .env.example: `cp .env.example .env`
- Step 2: Run docker compose: `docker compose up --build` or `docker compose up -d`
- Step 3: CD vào folder chatbot-backend: `cd chatbot-backend`
- Step 4: Tạo môi trường với anaconda qua lệnh: `conda create -n myenv python=3.11`
- Step 5: Activate môi trường: `conda activate myenv`
- Step 6: Install dependencies: `pip install -r requirements.txt`
- Step 7: Seed data vào database: `python app/database/seed.py`
- Step 8: Run backend: `uvicorn main:app --reload --host 0.0.0.0 --port 8030`

FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV APP_ENV=development \
    APP_DEBUG=true \
    PORT=8000 \
    DATABASE_PATH=/app/digital_farming.db \
    SECRET_KEY=change-me-in-production \
    JWT_ALGORITHM=HS256 \
    JWT_EXPIRY_HOURS=12

EXPOSE 8000

CMD ["sh", "-c", "python -m uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}"]

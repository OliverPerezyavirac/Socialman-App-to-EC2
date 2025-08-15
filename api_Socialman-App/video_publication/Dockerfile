FROM python:3.11-slim

LABEL maintainer="SocialMan Development"
LABEL service="video-publishing-service"
LABEL version="1.0.0"

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    pkg-config \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 5001

ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5001/health || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "4", "--worker-class", "sync", "--timeout", "60", "--keep-alive", "30", "--max-requests", "1000", "--max-requests-jitter", "100", "app:app"]

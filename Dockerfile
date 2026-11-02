FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_ROOT=/app \
    DATABASE_PATH=/app/data/bot.db \
    GUIDE_PATH=/app/documents/python-backend-roadmap.pdf

COPY pyproject.toml README.md ./
COPY src ./src
COPY documents ./documents

RUN pip install --no-cache-dir . \
    && mkdir -p /app/data

CMD ["ov-backend-bot"]

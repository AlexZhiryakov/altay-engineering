FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=7860 \
    DB_ENGINE=sqlite \
    SQLITE_PATH=/app/data/db.sqlite3

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libjpeg62-turbo zlib1g \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p /app/data \
    && DEBUG=True SECRET_KEY=build-time-only DB_ENGINE=sqlite SQLITE_PATH=/app/data/db.sqlite3 \
        python manage.py collectstatic --noinput \
    && DEBUG=True SECRET_KEY=build-time-only DB_ENGINE=sqlite SQLITE_PATH=/app/data/db.sqlite3 \
        python manage.py migrate --noinput \
    && DEBUG=True SECRET_KEY=build-time-only DB_ENGINE=sqlite SQLITE_PATH=/app/data/db.sqlite3 \
        python manage.py loaddata catalog

EXPOSE 7860

CMD ["python", "scripts/entrypoint.py"]

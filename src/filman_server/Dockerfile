FROM python:3.14.0-alpine

RUN apk update && apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    mariadb-dev \
    build-base

WORKDIR /app

# Copy dependency manifest
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy Alembic config and migrations (needed for runtime migrations)
COPY alembic.ini ./
COPY migrations ./migrations

# Copy application source
COPY src ./src

ENV PYTHONPATH=/app/src \
    RUN_MIGRATIONS_ON_STARTUP=1

CMD ["python", "-m", "filman_server.main"]
FROM python:3.11-alpine

RUN apk update && apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    mariadb-dev \
    build-base

WORKDIR /src/filman_server

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY /src/filman_server .

ENV PYTHONPATH=/src

CMD ["python3", "-m", "filman_server.main"]
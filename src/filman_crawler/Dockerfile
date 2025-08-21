FROM python:3.11-alpine

RUN apk update && apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    mariadb-dev \
    build-base

WORKDIR /src

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir watchdog

COPY /src/filman_server /src/filman_server
COPY /src/filman_crawler /src/filman_crawler

ENV PYTHONPATH=/src/filman_server:/src/filman_crawler

CMD [ "python3", "-m", "filman_crawler.main" ]
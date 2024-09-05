FROM python:3.11-slim-bullseye

RUN apt update
RUN apt install -y pkg-config default-libmysqlclient-dev build-essential

WORKDIR /src/filman_crawler

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY /src/filman_crawler .

ENV PYTHONPATH=/src

CMD [ "python3", "-m", "filman_crawler.main"]
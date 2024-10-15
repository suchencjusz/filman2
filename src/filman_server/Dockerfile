FROM python:3.12.7-slim-bullseye

RUN apt update
RUN apt install -y pkg-config default-libmysqlclient-dev build-essential

WORKDIR /src/filman_server

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY /src/filman_server .

ENV PYTHONPATH=/src

CMD [ "python3", "-m", "filman_server.main" ]
FROM python:3.11-slim-bullseye

RUN apt update
RUN apt install -y pkg-config default-libmysqlclient-dev build-essential

WORKDIR /FILMAN-DISCORD

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY /FILMAN-DISCORD .

CMD [ "python3", "-OO", "main.py"]
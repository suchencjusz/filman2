FROM python:3.11-slim-bullseye

WORKDIR /FILMAN-DISCORD

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY /FILMAN-DISCORD .

CMD [ "python3", "-OO", "main.py"]
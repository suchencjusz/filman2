FROM python:3.11-slim-bullseye

WORKDIR /FILMAN-CRAWLER

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY /FILMAN-CRAWLER .

CMD [ "python3", "main.py"]
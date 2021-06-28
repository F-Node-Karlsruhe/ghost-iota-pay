
FROM python:3.9.5-slim-buster

WORKDIR /app

RUN mkdir db

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

CMD [ "python", "-u" , "app.py"]
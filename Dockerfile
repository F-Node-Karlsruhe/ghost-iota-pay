
FROM python:3.9.5-slim-buster

WORKDIR /app

RUN mkdir db

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

# docker does not find the pip version
RUN pip install iota_client_python-0.2.0_alpha.3-cp36-abi3-linux_x86_64.whl

CMD [ "python", "-u" , "app.py"]
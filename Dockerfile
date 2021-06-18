
FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

# docker does not find the pip version
RUN pip install iota_client_python-0.2.0_alpha.3-cp36-abi3-linux_x86_64.whl

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
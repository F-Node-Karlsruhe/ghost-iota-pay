
FROM python:3.9.5-slim-buster

LABEL version="0.4"

LABEL source="https://github.com/F-Node-Karlsruhe/ghost-iota-pay"

LABEL maintainer="contact@f-node.de"

WORKDIR /app

RUN mkdir data

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

# docker does not find the pip version
RUN pip install iota_client_python-0.2.0_alpha.3-cp36-abi3-linux_x86_64.whl

CMD [ "python", "-u" , "app.py"]
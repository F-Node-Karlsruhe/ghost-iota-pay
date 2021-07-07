
FROM python:3.9.5-slim-buster

LABEL version="0.5"

LABEL source="https://github.com/F-Node-Karlsruhe/ghost-iota-pay"

LABEL maintainer="contact@f-node.de"

WORKDIR /app

RUN mkdir data

ARG FLASK_ENV="production"
ENV FLASK_ENV="${FLASK_ENV}" \
    FLASK_APP="ghostiotapay.app"

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

# docker does not find the pip version
RUN pip install iota_client_python-0.2.0_alpha.3-cp36-abi3-linux_x86_64.whl

EXPOSE 8000

CMD ["gunicorn", "-c", "python:config.gunicorn", "-k", "geventwebsocket.gunicorn.workers.GeventWebSocketWorker", "ghostiotapay.app:create_app()"]
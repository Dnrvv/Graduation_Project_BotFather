FROM python:3.9-buster
ENV BOT_NAME=$BOT_NAME

WORKDIR /src
COPY requirements.txt /src
RUN pip install -r requirements.txt
COPY . /src

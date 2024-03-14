FROM python:3.11-slim-bookworm

COPY ./src /opt/app
WORKDIR /opt/app
RUN pip install -r requirements.txt

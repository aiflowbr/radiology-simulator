FROM python:3.11-slim-bookworm

COPY ./requirements.txt /
COPY ./src /opt/app
WORKDIR /opt/app
RUN pip install -r /requirements.txt

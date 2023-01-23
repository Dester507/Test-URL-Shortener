FROM python:3.9-alpine

WORKDIR .

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


COPY requirements.txt .


RUN apk add build-base \
    && apk add libffi-dev


RUN pip install -r requirements.txt

COPY . .
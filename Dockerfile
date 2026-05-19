FROM python:3.13-slim AS build

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /opt/project

RUN apt-get update && \
    apt-get install -y --no-install-recommends netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /tmp/requirements.txt

RUN pip install --upgrade --no-cache-dir pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt

COPY ./entrypoint.sh /entrypoint.sh
COPY ./app /opt/project/app

RUN chmod +x /entrypoint.sh

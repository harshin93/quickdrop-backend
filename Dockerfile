FROM python:3.11-slim

WORKDIR /app

ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements-runtime.txt ./requirements-runtime.txt

RUN pip install --no-cache-dir -r requirements-runtime.txt

COPY . .


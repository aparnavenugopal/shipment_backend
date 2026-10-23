FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . ./training

EXPOSE 10000
CMD ["sh", "-c", "uvicorn training.main:app --host 0.0.0.0 --port ${PORT:-10000}"]

FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y g++ openjdk-17-jdk && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

EXPOSE 10000

CMD ["python", "app.py"]
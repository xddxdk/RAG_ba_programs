FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git && apt-get clean

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app

CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]
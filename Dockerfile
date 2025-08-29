FROM python:3.11-slim

# system deps for soundfile + optional espeak-ng
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 espeak-ng && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .

# Render sets $PORT. Use it if present.
CMD ["sh","-c","uvicorn app:app --host 0.0.0.0 --port ${PORT:-10000}"]

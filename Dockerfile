FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 espeak-ng && \
    rm -rf /var/lib/apt/lists/*

ENV PIP_NO_CACHE_DIR=1 PIP_ONLY_BINARY=:all: \
    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app.py .

# Spaces injects PORT (usually 7860). Bind 0.0.0.0:$PORT.
CMD ["sh","-c","uvicorn app:app --host 0.0.0.0 --port ${PORT:-7860}"]

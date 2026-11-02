FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    COQUI_TOS_AGREED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
# Обновляем pip: штатный pip 23.0.1 в python:3.10-slim отклоняет wheel
# typing_extensions («inconsistent Name») и ломает установку torch
RUN pip install --no-cache-dir --upgrade pip
# PyTorch с поддержкой CUDA 12.1 — ставим отдельно из официального индекса,
# иначе PyPI отдаст CPU-версию и видеокарта не будет использоваться
RUN pip install --no-cache-dir torch==2.1.0+cu121 torchaudio==2.1.0+cu121 \
    --index-url https://download.pytorch.org/whl/cu121 \
    --extra-index-url https://pypi.org/simple
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

RUN mkdir -p /input /output /reference

CMD ["python", "app/main.py"]

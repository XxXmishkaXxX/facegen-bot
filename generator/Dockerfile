FROM python:3.11-slim

# ---------- system deps ---------- #
RUN apt-get update && apt-get install -y --no-install-recommends \
        git gcc g++ build-essential wget \
    && rm -rf /var/lib/apt/lists/*

# ---------- app ---------- #
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# ---------- preload HF models ---------- #
ENV HF_HUB_DISABLE_TELEMETRY=1 \
    TRANSFORMERS_CACHE=/data/hf_cache \
    HF_HOME=/data/hf_cache

CMD ["python", "main.py"]

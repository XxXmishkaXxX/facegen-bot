FROM nvidia/cuda:12.2.0-base-ubuntu22.04

# Установка Python и всех зависимостей в одном слое
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3.11 python3.11-dev python3.11-distutils python3-pip \
        git gcc g++ build-essential wget \
    && rm -rf /var/lib/apt/lists/*

# ---------- app ---------- #
WORKDIR /app
COPY requirements.txt .

# Установка зависимостей Python
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
# ---------- preload HF models ---------- #
ENV HF_HUB_DISABLE_TELEMETRY=1 \
    TRANSFORMERS_CACHE=/data/hf_cache \
    HF_HOME=/data/hf_cache
RUN echo "import torch; torch.cuda.empty_cache()" > clear_gpu_cache.py

CMD ["python3", "main.py"]

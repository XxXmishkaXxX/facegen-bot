FROM nvidia/cuda:12.2.0-base-ubuntu22.04

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 python3.11-dev python3.11-distutils python3-pip \
    build-essential gcc g++ make cmake \
    git wget \
    libffi-dev libssl-dev pkg-config \
    **libgl1 libglib2.0-0** \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .

# Обновляем pip и сопутствующие инструменты
RUN python3.11 -m pip install --upgrade pip setuptools wheel

# Устанавливаем Python-зависимости из requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
ENV HF_HUB_DISABLE_TELEMETRY=1 \
    TRANSFORMERS_CACHE=/data/hf_cache \
    HF_HOME=/data/hf_cache

RUN echo "import torch; torch.cuda.empty_cache()" > clear_gpu_cache.py

CMD ["python3.11", "main.py"]

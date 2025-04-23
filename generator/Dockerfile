FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
git gcc g++ build-essential wget \
&& rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV HF_HUB_DISABLE_TELEMETRY=1
RUN python - << 'PY'
from huggingface_hub import snapshot_download
snapshot_download("runwayml/stable-diffusion-v1-5", local_dir_use_symlinks=False)
snapshot_download("SG161222/Realistic_Vision_V4.0", local_dir_use_symlinks=False)
PY

ENV TRANSFORMERS_CACHE=/data/hf_cache \
HF_HOME=/data/hf_cache

CMD ["python", "main.py"]

    
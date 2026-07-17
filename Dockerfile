# ============================================================
# Dockerfile
# AI-Powered Financial Fraud Detection System
# Streamlit dashboard with auto-download of pre-trained assets
# ============================================================

# ── Base image: Python 3.11 slim (Bookworm for stability) ─────────
FROM python:3.11-slim-bookworm

# ── Labels ───────────────────────────────────────────────────
LABEL maintainer="AI Fraud Guard"
LABEL description="Multi-modal fraud detection: XGBoost + DistilBERT + Siamese ResNet18"
LABEL version="1.0"

# ── System dependencies ───────────────────────────────────────
# libgl1 + libglib2.0-0 : required by OpenCV (cv2)
# libgomp1              : required by XGBoost parallel inference
# curl                  : health-check and general debugging
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
        libgomp1 \
        curl \
    && rm -rf /var/lib/apt/lists/*

# ── Working directory ─────────────────────────────────────────
WORKDIR /app

# ── Python dependencies (cached layer) ───────────────────────
# Copy requirements first so Docker caches this layer unless
# requirements change — code changes don't bust the pip cache.
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu \
 && pip install --no-cache-dir -r requirements.txt \
 && pip install --no-cache-dir gdown          # needed by setup_assets.py

# ── Copy application source ───────────────────────────────────
COPY . .

# ── Expose FastAPI port ─────────────────────────────────────
EXPOSE 8000

# ── Environment variables (override via docker-compose or -e) ─
# Paste your Google Drive share URLs or bare file IDs here.
# These are read by setup_assets.py at container startup.
ENV MODELS_GDRIVE_URL="https://drive.google.com/file/d/1m-82bqvhosy8sZCjXA3Q1F0mfRkDGMl_/view?usp=sharing"
ENV DATA_GDRIVE_URL=""
# Set DATA_GDRIVE_URL only if you want the data folder too.
# Leave empty ("") to skip data download (not needed to run the dashboard).

# Skip data download by default — only models are needed for inference
ENV SETUP_ASSETS_ARGS="--models-only"

# ── Entrypoint ────────────────────────────────────────────────
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

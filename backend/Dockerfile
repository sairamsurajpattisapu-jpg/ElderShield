# =====================================================================
# ELDERSHIELD PRODUCTION BACKEND DOCKERFILE
# Multi-stage container build with non-root security and health checks
# =====================================================================

FROM python:3.11-slim AS builder

WORKDIR /app

# Install build tools and ffmpeg for audio processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final Runtime Stage
FROM python:3.11-slim AS runtime

WORKDIR /app

# Install runtime ffmpeg & libsndfile1 for whisper audio ingestion
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user with home directory
RUN groupadd -r eldershield && useradd -m -r -g eldershield -u 1001 eldershield

# Copy installed python packages from builder
COPY --from=builder /root/.local /home/eldershield/.local
ENV PATH=/home/eldershield/.local/bin:$PATH
ENV HF_HOME=/home/eldershield/.cache/huggingface

# Copy application source code
COPY --chown=eldershield:eldershield . /app

USER eldershield

# Expose API port
EXPOSE 8000

# Container Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Production server start with dynamic PORT support
CMD ["sh", "-c", "python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]

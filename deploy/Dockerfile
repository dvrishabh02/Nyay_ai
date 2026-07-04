# Backend image for Hugging Face Spaces (Docker SDK).
# Built from a curated export (see scripts/prepare_hf_space.sh) that contains
# only api/, rag/, ingestion/, data/index/, and requirements.txt — not the
# full monorepo (avoids dragging the multi-GB raw legal corpus into the image).

FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/app/.cache/huggingface

COPY requirements.txt .
RUN pip install -r requirements.txt

# Bake the embedding + reranker model weights into the image so the
# container doesn't need to download them on every cold start.
RUN python -c "\
from sentence_transformers import SentenceTransformer, CrossEncoder; \
SentenceTransformer('intfloat/e5-base-v2'); \
CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')"

COPY api/ ./api/
COPY rag/ ./rag/
COPY ingestion/ ./ingestion/
COPY data/index/ ./data/index/

# Hugging Face Spaces (Docker SDK) expects the app on port 7860.
EXPOSE 7860

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "7860"]

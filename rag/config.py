"""
RAG chain configuration — single source of truth for query-time settings.

Reuses index paths and embedding constants from the ingestion config so there's
no duplication; adds retrieval/rerank/generation tunables and Groq credentials.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Reuse ingestion constants (index paths, embedding model, query prefix)
from ingestion.config import (  # noqa: F401  (re-exported for convenience)
    BM25_INDEX_FILE,
    EMBEDDING_MODEL,
    FAISS_INDEX_FILE,
    METADATA_FILE,
    QUERY_PREFIX,
)

# Load .env from project root
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# ── Retrieval ──
RETRIEVE_K = 20          # candidates fetched per system (FAISS, BM25) before fusion
RRF_K = 60               # Reciprocal Rank Fusion constant

# ── Reranking ──
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
RERANK_TOP_N = 8         # chunks kept after rerank → fed to the LLM

# ── Confidence thresholds (top reranker score → label) ──
# ms-marco cross-encoder emits unbounded logits; calibrate against real queries.
CONFIDENCE_HIGH = 5.0
CONFIDENCE_MEDIUM = 0.0

# ── Generation (Groq, OpenAI-compatible) ──
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
GENERATION_TEMPERATURE = 0.0
GENERATION_MAX_TOKENS = 1024

# ── Output ──
DISCLAIMER = (
    "This is general legal information, not legal advice. "
    "Laws change and every situation is different — consult a qualified lawyer "
    "before acting."
)
NO_CONTEXT_FALLBACK = "I don't have enough information"

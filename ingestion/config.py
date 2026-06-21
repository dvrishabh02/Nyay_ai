"""
Central configuration for the ingestion pipeline.
All paths, constants, and tunables live here — single source of truth.
"""

from pathlib import Path

# ── Project Root ──
PROJECT_ROOT = Path(__file__).parent.parent

# ── Data Paths ──
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
INDEX_DIR = PROJECT_ROOT / "data" / "index"

# ── Raw Data Sources (parquets to ingest for first launch) ──
PARQUET_SOURCES = {
    "sc_chunked": {
        "path": RAW_DATA_DIR / "judgments" / "supreme_court" / "hf_chunked" / "train.parquet",
        "doc_type": "judgment",
        "court": "supreme_court",
        "pre_chunked": True,
        "description": "20,961 pre-chunked SC judgment passages",
    },
    "legal_chunks": {
        "path": RAW_DATA_DIR / "judgments" / "hf_legal_chunks" / "train.parquet",
        "doc_type": "judgment",
        "court": "supreme_court",
        "pre_chunked": True,
        "description": "1,469 RAG-ready legal chunks",
    },
    "central_acts": {
        "path": RAW_DATA_DIR / "legislation" / "hf_acts" / "central.parquet",
        "doc_type": "act",
        "court": None,
        "pre_chunked": False,
        "description": "883 central acts with full Markdown text",
    },
    "ap_acts": {
        "path": RAW_DATA_DIR / "legislation" / "hf_acts" / "andhra_pradesh.parquet",
        "doc_type": "act",
        "court": None,
        "pre_chunked": False,
        "description": "Andhra Pradesh state acts",
    },
    "arunachal_acts": {
        "path": RAW_DATA_DIR / "legislation" / "hf_acts" / "arunachal_pradesh.parquet",
        "doc_type": "act",
        "court": None,
        "pre_chunked": False,
        "description": "Arunachal Pradesh state acts",
    },
    "andaman_acts": {
        "path": RAW_DATA_DIR / "legislation" / "hf_acts" / "andaman_and_nicobar_islands.parquet",
        "doc_type": "act",
        "court": None,
        "pre_chunked": False,
        "description": "Andaman & Nicobar Islands acts",
    },
}

# ── QA Pairs (saved as prompt data, NOT indexed in FAISS) ──
QA_SOURCES = {
    "indian_law_qa": {
        "path": RAW_DATA_DIR / "legislation" / "hf_indian_law" / "train.parquet",
        "rows": 24_607,
    },
    "constitution_qa": {
        "path": RAW_DATA_DIR / "legislation" / "hf_constitution_qa" / "train.parquet",
        "rows": 3_311,
    },
    "constitution_ipc": {
        "path": RAW_DATA_DIR / "legislation" / "hf_constitution_ipc_instruct" / "train.parquet",
        "rows": 6_077,
    },
    "constitution": {
        "path": RAW_DATA_DIR / "legislation" / "hf_constitution" / "train.parquet",
        "rows": 933,
    },
}

# ── Chunking Config ──
CHUNK_SIZE_TOKENS = 700
CHUNK_OVERLAP_TOKENS = 105       # ~15% of chunk_size
MIN_CHUNK_TOKENS = 200           # Drop chunks smaller than this
CHUNK_SEPARATORS = [
    "\n## ",                      # Markdown H2
    "\n### ",                     # Markdown H3
    "\nSection ",                 # Act sections
    "\nArticle ",                 # Constitution articles
    "\nORDER",                    # Judgment orders
    "\n\n",                       # Paragraphs
    "\n",                         # Lines
    ". ",                         # Sentences
]

# ── Embedding Config ──
EMBEDDING_MODEL = "intfloat/e5-base-v2"
EMBEDDING_DIM = 768
EMBEDDING_PREFIX = "passage: "   # Required by e5 models
QUERY_PREFIX = "query: "         # Used at search time
EMBEDDING_BATCH_SIZE = 256

# ── Index Files ──
FAISS_INDEX_FILE = INDEX_DIR / "index.faiss"
BM25_INDEX_FILE = INDEX_DIR / "bm25.pkl"
METADATA_FILE = INDEX_DIR / "metadata.pkl"
MANIFEST_FILE = INDEX_DIR / "manifest.json"

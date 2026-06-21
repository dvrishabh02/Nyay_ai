# Nyay.AI — First Launch Ingestion Flow

> **Goal**: Raw data on disk → FAISS + BM25 index files → ready to serve queries
> **Run once**, rebuild only when adding new data

---

## 1. What We Have on Disk (12 GB)

### A. Parquet Files (HuggingFace) — Small, Structured

| # | File | Rows | Size | What's Inside |
|---|------|------|------|---------------|
| 1 | `judgments/supreme_court/hf_chunked/train.parquet` | 20,961 | 3.4 MB | Pre-chunked SC judgment passages |
| 2 | `judgments/hf_legal_chunks/train.parquet` | 1,469 | 368 KB | Pre-chunked legal text (RAG-ready) |
| 3 | `legislation/hf_acts/central.parquet` | 883 | 23 MB | Full text of 883 central acts (Markdown) |
| 4 | `legislation/hf_acts/andhra_pradesh.parquet` | ~323 | 3.8 MB | AP state acts |
| 5 | `legislation/hf_acts/arunachal_pradesh.parquet` | ~1,111 | 6.9 MB | Arunachal state acts |
| 6 | `legislation/hf_acts/andaman_and_nicobar_islands.parquet` | ~66 | 3.1 MB | A&N acts |
| 7 | `legislation/hf_indian_law/train.parquet` | 24,607 | 4.4 MB | Legal QA pairs |
| 8 | `legislation/hf_constitution_qa/train.parquet` | 3,311 | 2.4 MB | Constitution QA pairs |
| 9 | `legislation/hf_constitution_ipc_instruct/train.parquet` | 6,077 | 1.1 MB | Constitution + IPC QA |
| 10 | `legislation/hf_constitution/train.parquet` | 933 | 184 KB | Constitution QA |
| 11 | `schemes/hf_myscheme/train.parquet` | 3 | 4 KB | Scheme PDF references |

### B. Text Files (Kaggle) — Large, Unstructured

| # | Path | Files | Size | What's Inside |
|---|------|-------|------|---------------|
| 12 | `judgments/supreme_court/kaggle_1950_2024/` | 26,689 .txt | 6.8 GB | Full SC judgment text (1950-2025) |
| 13 | `judgments/supreme_court/kaggle_full/pdfs/` | 48,294 .pdf | 5.4 GB | Full SC judgment PDFs |
| 13b | `judgments/supreme_court/kaggle_full/judgments.csv` | 1 CSV | 8.2 MB | Metadata for all PDFs |
| 14 | `judgments/high_courts/kaggle_hc_cases/` | 4 CSVs | 84 KB | HC case metadata |

---

## 2. What Goes Where (The Decision)

### INTO FAISS INDEX (semantic search) — only real legal text

| Source | What | Chunks (est.) | Why |
|--------|------|---------------|-----|
| #1 SC Chunked (HF) | 20,961 pre-chunked passages | **20,961** | Already chunked, highest quality |
| #2 Legal Chunks (HF) | 1,469 pre-chunked passages | **1,469** | Already RAG-ready |
| #3 Central Acts (HF) | 883 full acts → chunk | **~7,000** | Core legal text, every query needs this |
| #4-6 State Acts (HF) | ~1,500 acts → chunk | **~5,000** | AP, Arunachal, A&N acts |
| #12 SC Judgments (Kaggle) | Top 5,000 recent (2020-2025) → chunk | **~50,000** | Most relevant recent judgments |
| **TOTAL** | | **~85,000 chunks** | |

**FAISS size**: 85,000 × 1024 dim × 4 bytes = **~340 MB** (float32) or **~170 MB** (float16)

### INTO PROMPT CONTEXT (not FAISS) — QA pairs for answer quality

| Source | What | Rows | How Used |
|--------|------|------|----------|
| #7 Indian Law QA | Legal QA pairs | 24,607 | Few-shot examples in system prompt |
| #8 Constitution QA | Constitution QA pairs | 3,311 | Few-shot examples |
| #9 Constitution+IPC | Instruct QA pairs | 6,077 | Few-shot examples |
| #10 Constitution | Constitution QA | 933 | Few-shot examples |

These are **question-answer pairs**, not legal source text. They help the LLM answer better but shouldn't be "retrieved" as citations. Store in a **SQLite DB** or **JSON file** for prompt engineering.

### DEFERRED (not indexed for first launch)

| Source | Why Deferred |
|--------|-------------|
| #12 Remaining 21,689 SC judgments (1950-2019) | Too many, old, add post-launch |
| #13 48,294 SC PDFs | Need OCR, massive, add Tier 2 judgments from text files instead |
| #14 HC metadata CSVs | Metadata only, no judgment text |
| #11 MyScheme | Only 3 rows, PDF references — not useful yet |

---

## 3. The Ingestion Pipeline (Step by Step)

```
                         INGESTION FLOW
                         ==============

STEP 1                   STEP 2                STEP 3
LOAD & PARSE             CHUNK                 QUALITY CHECK
────────────             ─────                 ─────────────
                         
  Parquets ──┐           ┌─ Already chunked    ┌─ Length: 200-1000 tokens
             │           │  (HF #1, #2)        │  Drop if < 200
  Text ──────┤──► Clean ─┤                     ├─ Language: EN or HI only
  files      │   UTF-8   │  Needs chunking     │  Drop others
             │   remove  │  (Acts #3-6,        ├─ Dedup: SHA-256 hash
  (skip      │   noise   │   Judgments #12)     │  Remove duplicates
   PDFs)     │           │                     ├─ Empty: drop whitespace
             │           │  700 tokens         │  only chunks
             │           │  15% overlap        └─ Legal relevance check
             │           │  Section-aware
             │           │
             ▼           ▼                     ▼

STEP 4                   STEP 5                STEP 6
ENRICH METADATA          EMBED                 BUILD INDEX
───────────────          ─────                 ───────────

  For each chunk:        multilingual-e5-large  ┌─ FAISS IndexFlatIP
  {                      1024 dimensions        │  (inner product)
    doc_type: "act"      batch size: 256        │  → index.faiss
    court: "SC"                                 │
    domain: "property"   GPU if available       ├─ BM25 (rank_bm25)
    year: 2024           else CPU (~2-4 hrs     │  → bm25.pkl
    citation: "..."      for 85K chunks)        │
    source_file: "..."                          ├─ Metadata store
  }                                             │  → metadata.pkl
                                                │  (chunk text + metadata)
                                                │
                                                └─ Stats + manifest
                                                   → index_manifest.json
```

---

## 4. Detailed Steps

### Step 1: Load & Parse

```
┌──────────────────────────────────────────────────────────────────┐
│ STEP 1: LOAD RAW DATA                                           │
│                                                                  │
│ Source A: HuggingFace Parquets (pandas)                          │
│ ─────────────────────────────────────────                        │
│ df = pd.read_parquet("hf_chunked/train.parquet")                │
│ df = pd.read_parquet("hf_legal_chunks/train.parquet")           │
│ df = pd.read_parquet("hf_acts/central.parquet")                 │
│ df = pd.read_parquet("hf_acts/andhra_pradesh.parquet")          │
│ df = pd.read_parquet("hf_acts/arunachal_pradesh.parquet")       │
│ df = pd.read_parquet("hf_acts/andaman_and_nicobar_islands.parquet") │
│                                                                  │
│ Source B: Kaggle SC Judgments (text files)                        │
│ ─────────────────────────────────────────                        │
│ Only recent 5,000 files (2020-2025):                             │
│ for year in [2020, 2021, 2022, 2023, 2024, 2025]:               │
│     for txt_file in Path(f"kaggle_1950_2024/{year}/").glob("*"): │
│         text = txt_file.read_text(encoding="utf-8")              │
│                                                                  │
│ Source C: Skip for now                                           │
│ ─────────────────────────────────────────                        │
│ ❌ PDFs (48K) — too slow, need OCR                               │
│ ❌ HC metadata CSVs — no judgment text                           │
│ ❌ QA pairs — saved separately, not for FAISS                    │
│                                                                  │
│ CLEANING:                                                        │
│ - Force UTF-8 encoding                                           │
│ - Strip headers/footers (page numbers, court headers)            │
│ - Normalize whitespace (collapse multiple \n, \t)                │
│ - Remove non-text artifacts (form feeds, control chars)          │
└──────────────────────────────────────────────────────────────────┘
```

### Step 2: Chunk

```
┌──────────────────────────────────────────────────────────────────┐
│ STEP 2: CHUNKING                                                 │
│                                                                  │
│ Path A: Already Chunked (pass through)                           │
│ ──────────────────────────────────────                           │
│ HF SC Chunked (#1): 20,961 chunks → pass through as-is          │
│ HF Legal Chunks (#2): 1,469 chunks → pass through as-is         │
│                                                                  │
│ Path B: Needs Chunking (RecursiveCharacterTextSplitter)          │
│ ──────────────────────────────────────────────────────           │
│ Central Acts (#3): 883 full acts → ~7,000 chunks                 │
│ State Acts (#4-6): ~1,500 acts → ~5,000 chunks                  │
│ SC Judgments (#12): 5,000 text files → ~50,000 chunks            │
│                                                                  │
│ CHUNKING CONFIG:                                                 │
│ ┌──────────────────────────────────┐                             │
│ │ chunk_size     = 700 tokens      │                             │
│ │ chunk_overlap  = 105 tokens (15%)│                             │
│ │ min_chunk_size = 200 tokens      │ ← drop tiny chunks         │
│ │ separators = [                   │                             │
│ │   "\n## ",       ← H2 headings  │                             │
│ │   "\n### ",      ← H3 headings  │                             │
│ │   "\nSection ",  ← Act sections │                             │
│ │   "\nArticle ",  ← Constitution │                             │
│ │   "\n\n",        ← Paragraphs   │                             │
│ │   "\n",          ← Lines        │                             │
│ │   ". ",          ← Sentences    │                             │
│ │ ]                                │                             │
│ └──────────────────────────────────┘                             │
│                                                                  │
│ This respects document structure:                                │
│ - Sections of an Act stay together                               │
│ - Paragraphs of a judgment stay together                         │
│ - Overlap ensures no info is lost at boundaries                  │
└──────────────────────────────────────────────────────────────────┘
```

### Step 3: Quality Checks

```
┌──────────────────────────────────────────────────────────────────┐
│ STEP 3: QUALITY FILTERS (applied to every chunk)                 │
│                                                                  │
│ Filter 1: LENGTH                                                 │
│   token_count = len(tiktoken.encode(chunk))                      │
│   if token_count < 200: DROP  (too short, no useful content)     │
│   if token_count > 1000: RE-CHUNK  (shouldn't happen)            │
│                                                                  │
│ Filter 2: LANGUAGE                                               │
│   lang = langdetect.detect(chunk)                                │
│   if lang not in ["en", "hi"]: DROP                              │
│                                                                  │
│ Filter 3: DEDUP                                                  │
│   hash = sha256(chunk.strip().lower())                           │
│   if hash in seen_hashes: DROP                                   │
│   seen_hashes.add(hash)                                          │
│                                                                  │
│ Filter 4: NOT EMPTY                                              │
│   if chunk.strip() == "": DROP                                   │
│                                                                  │
│ Filter 5: LEGAL RELEVANCE (soft check)                           │
│   legal_keywords = ["section", "act", "court", "judgment",       │
│     "article", "order", "petition", "plaintiff", "defendant",    │
│     "hereby", "whereas", "tribunal", "appeal", "bail",           │
│     "constitution", "provision", "statute", "accused"]           │
│   if count(legal_keywords in chunk) == 0: FLAG for review        │
│                                                                  │
│ Expected drop rate: ~10-15% of chunks                            │
└──────────────────────────────────────────────────────────────────┘
```

### Step 4: Metadata Enrichment

```
┌──────────────────────────────────────────────────────────────────┐
│ STEP 4: ADD METADATA TO EVERY CHUNK                              │
│                                                                  │
│ For ACTS (hf_acts):                                              │
│ {                                                                │
│   "chunk_id": "act_central_045_chunk_003",                       │
│   "text": "Section 138. Dishonour of cheque for...",             │
│   "doc_type": "act",                                             │
│   "court": null,                                                 │
│   "jurisdiction": "central",         ← from filename            │
│   "domain": "criminal",              ← keyword classify         │
│   "year": null,                                                  │
│   "title": "Negotiable Instruments Act, 1881",                   │
│   "source": "hf_acts",                                           │
│   "source_file": "central.parquet",                              │
│   "chunk_index": 3,                                              │
│   "total_chunks": 12                                             │
│ }                                                                │
│                                                                  │
│ For SC JUDGMENTS (kaggle text files):                             │
│ {                                                                │
│   "chunk_id": "sc_2024_case001_chunk_007",                       │
│   "text": "The tenant has a right to...",                        │
│   "doc_type": "judgment",                                        │
│   "court": "supreme_court",                                      │
│   "jurisdiction": "central",                                     │
│   "domain": "property",              ← keyword classify         │
│   "year": 2024,                       ← from folder name        │
│   "title": null,                      ← extract from first line │
│   "source": "kaggle_1950_2024",                                  │
│   "source_file": "2024/case_001.txt",                            │
│   "chunk_index": 7,                                              │
│   "total_chunks": 25                                             │
│ }                                                                │
│                                                                  │
│ For PRE-CHUNKED (hf_chunked, hf_legal_chunks):                   │
│ {                                                                │
│   "chunk_id": "hf_sc_00001",                                    │
│   "text": "<original text from parquet>",                        │
│   "doc_type": "judgment",                                        │
│   "court": "supreme_court",                                      │
│   "domain": "general",               ← auto-classify later     │
│   "year": null,                       ← extract if available    │
│   "source": "hf_chunked",                                       │
│   "chunk_index": 0,                                              │
│   "total_chunks": 1                                              │
│ }                                                                │
│                                                                  │
│ DOMAIN CLASSIFIER (simple keyword-based for MVP):                │
│ ────────────────────────────────────────────────                 │
│ "property"       → rent, tenant, landlord, eviction, mutation    │
│ "consumer"       → consumer, defective, refund, insurance        │
│ "criminal"       → FIR, bail, accused, prosecution, BNS, IPC    │
│ "labour"         → salary, termination, PF, ESIC, employer      │
│ "family"         → maintenance, divorce, custody, domestic       │
│ "constitutional" → article, fundamental, writ, constitution     │
│ "tax"            → GST, income tax, assessment, tribunal        │
│ "general"        → (default if no match)                         │
└──────────────────────────────────────────────────────────────────┘
```

### Step 5: Embed

```
┌──────────────────────────────────────────────────────────────────┐
│ STEP 5: GENERATE EMBEDDINGS                                      │
│                                                                  │
│ MODEL: intfloat/multilingual-e5-large                            │
│ DIMENSIONS: 1024                                                 │
│ PREFIX: "passage: " (required by e5 models)                      │
│                                                                  │
│ PROCESS:                                                         │
│ ─────────                                                        │
│ from sentence_transformers import SentenceTransformer             │
│                                                                  │
│ model = SentenceTransformer("intfloat/multilingual-e5-large")    │
│                                                                  │
│ # Batch embed all chunks                                         │
│ texts = ["passage: " + chunk["text"] for chunk in all_chunks]    │
│ embeddings = model.encode(                                        │
│     texts,                                                       │
│     batch_size=256,                                              │
│     show_progress_bar=True,                                      │
│     normalize_embeddings=True,   ← for cosine sim via dot product│
│ )                                                                │
│                                                                  │
│ HARDWARE:                                                        │
│ ──────────                                                       │
│ GPU (if available): ~30 min for 85K chunks                       │
│ CPU (M1/M2 Mac):   ~2-4 hours for 85K chunks                    │
│ CPU (Intel):        ~4-6 hours for 85K chunks                    │
│                                                                  │
│ TIP: Save embeddings to a .npy file after generation             │
│ so you never have to re-embed the same data:                     │
│ np.save("data/processed/embeddings.npy", embeddings)             │
└──────────────────────────────────────────────────────────────────┘
```

### Step 6: Build Index

```
┌──────────────────────────────────────────────────────────────────┐
│ STEP 6: BUILD FAISS + BM25 INDICES                               │
│                                                                  │
│ A. FAISS INDEX (dense vectors)                                   │
│ ──────────────────────────────                                   │
│ import faiss                                                     │
│ import numpy as np                                               │
│                                                                  │
│ dim = 1024                                                       │
│ index = faiss.IndexFlatIP(dim)   ← inner product (cosine sim)   │
│ index.add(embeddings)            ← numpy array (85K × 1024)     │
│                                                                  │
│ faiss.write_index(index, "data/index/index.faiss")               │
│                                                                  │
│ B. BM25 INDEX (sparse keywords)                                  │
│ ───────────────────────────────                                  │
│ from rank_bm25 import BM25Okapi                                  │
│ import pickle                                                    │
│                                                                  │
│ tokenized = [chunk["text"].lower().split() for chunk in chunks]  │
│ bm25 = BM25Okapi(tokenized)                                     │
│                                                                  │
│ with open("data/index/bm25.pkl", "wb") as f:                     │
│     pickle.dump(bm25, f)                                         │
│                                                                  │
│ C. METADATA STORE                                                │
│ ─────────────────                                                │
│ metadata = [                                                     │
│   {"chunk_id": "...", "text": "...", "doc_type": "...", ...},    │
│   ...                                                            │
│ ]                                                                │
│                                                                  │
│ with open("data/index/metadata.pkl", "wb") as f:                 │
│     pickle.dump(metadata, f)                                     │
│                                                                  │
│ D. MANIFEST (build stats)                                        │
│ ─────────────────────────                                        │
│ {                                                                │
│   "built_at": "2026-06-21T17:30:00",                             │
│   "total_chunks": 85000,                                         │
│   "sources": {                                                   │
│     "hf_chunked": 20961,                                        │
│     "hf_legal_chunks": 1469,                                    │
│     "hf_acts_central": 7000,                                    │
│     "hf_acts_state": 5000,                                      │
│     "kaggle_sc_2020_2025": 50000                                │
│   },                                                             │
│   "embedding_model": "intfloat/multilingual-e5-large",           │
│   "embedding_dim": 1024,                                         │
│   "chunk_size": 700,                                             │
│   "chunk_overlap": 105,                                          │
│   "faiss_index_type": "IndexFlatIP",                             │
│   "files": {                                                     │
│     "index.faiss": "340 MB",                                     │
│     "bm25.pkl": "50 MB",                                        │
│     "metadata.pkl": "100 MB",                                   │
│     "embeddings.npy": "340 MB"                                  │
│   }                                                              │
│ }                                                                │
│                                                                  │
│ OUTPUT FILES (saved to data/index/):                              │
│ ────────────────────────────────────                              │
│ data/index/                                                      │
│ ├── index.faiss        (~170-340 MB)                             │
│ ├── bm25.pkl           (~50 MB)                                  │
│ ├── metadata.pkl       (~100 MB)                                 │
│ ├── embeddings.npy     (~340 MB, backup)                         │
│ └── manifest.json      (<1 KB)                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## 5. Full Pipeline Summary

```
RAW DATA (12 GB on disk)
    │
    ├── HF Parquets (10 files, ~45 MB)
    │     ├── 2 pre-chunked datasets ──────────► PASS THROUGH ──┐
    │     ├── 4 act datasets (central + 3 state) ► CHUNK ───────┤
    │     └── 4 QA datasets ───────────────────► SAVE AS JSON   │ (not FAISS)
    │                                             (prompt data)  │
    ├── Kaggle Text (26,689 files, 6.8 GB)                      │
    │     └── Top 5,000 (2020-2025 only) ──────► CHUNK ─────────┤
    │                                                            │
    ├── Kaggle PDFs (48K, 5.4 GB) ──► SKIP (first launch)       │
    └── HC CSVs (84 KB) ───────────► SKIP (metadata only)       │
                                                                 │
                                                                 ▼
                                                    ~85,000 chunks
                                                         │
                                            ┌────────────┤
                                            ▼            ▼
                                      Quality        Metadata
                                      Filters        Enrichment
                                      (~10-15%       (doc_type,
                                       dropped)       court,
                                            │         domain,
                                            │         year)
                                            │            │
                                            └─────┬──────┘
                                                  ▼
                                            ~72,000-76,000
                                            clean chunks
                                                  │
                                    ┌─────────────┤
                                    ▼             ▼
                              Embed (e5)     Tokenize
                              1024-dim       (whitespace)
                                    │             │
                                    ▼             ▼
                              FAISS Index    BM25 Index
                              index.faiss    bm25.pkl
                              (~170-340 MB)  (~50 MB)
                                    │             │
                                    └──────┬──────┘
                                           ▼
                                    metadata.pkl
                                    (~100 MB)
                                           │
                                           ▼
                                  data/index/ folder
                                  ==================
                                  Total: ~400-550 MB on disk
                                  RAM at runtime: ~500 MB
                                  Load time on startup: ~10s
```

---

## 6. Script Structure

The pipeline will be implemented as:

```
scripts/
└── build_index.py          ← Main entry point

ingestion/
├── __init__.py
├── parsers/
│   ├── __init__.py
│   ├── parquet_parser.py   ← Load HF parquet files
│   └── text_parser.py      ← Load Kaggle text files
├── chunkers/
│   ├── __init__.py
│   └── legal_chunker.py    ← RecursiveCharacterTextSplitter with legal separators
├── enrichers/
│   ├── __init__.py
│   ├── metadata.py         ← Add doc_type, court, domain, year
│   └── domain_classifier.py ← Keyword-based domain tagging
├── quality/
│   ├── __init__.py
│   └── filters.py          ← Length, language, dedup, empty checks
├── embedders/
│   ├── __init__.py
│   └── e5_embedder.py      ← multilingual-e5-large wrapper
└── indexers/
    ├── __init__.py
    ├── faiss_builder.py     ← Build + save FAISS index
    └── bm25_builder.py      ← Build + save BM25 index

data/
├── raw/                     ← Source data (already here)
├── processed/               ← Intermediate outputs (chunks JSON)
└── index/                   ← Final index files (FAISS + BM25 + metadata)
```

---

## 7. Run Command

```bash
# Full build (first time — ~2-4 hours on CPU)
python scripts/build_index.py --all

# Only rebuild from existing chunks (skip parsing — ~30 min)
python scripts/build_index.py --embed-only

# Add new data incrementally
python scripts/build_index.py --source kaggle_sc --years 2019,2018
```

---

## 8. Time Estimates

| Step | CPU (M1/M2 Mac) | GPU (Colab/Cloud) |
|------|-----------------|-------------------|
| Parse + Clean | ~5 min | ~5 min |
| Chunk | ~10 min | ~10 min |
| Quality filters | ~2 min | ~2 min |
| Metadata enrichment | ~5 min | ~5 min |
| **Embedding (85K chunks)** | **~2-4 hours** | **~30 min** |
| Build FAISS index | ~1 min | ~1 min |
| Build BM25 index | ~5 min | ~5 min |
| **TOTAL** | **~3-5 hours** | **~1 hour** |

> Embedding is the bottleneck. Everything else is fast.
> Consider using Google Colab (free GPU) for the embedding step.

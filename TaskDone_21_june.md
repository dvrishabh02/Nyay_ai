# Nyay.AI — Task Log: 21 June 2026

> **Branch**: `first-launch`
> **Session**: ~2 hours (5:18 PM - 6:44 PM IST)

---

## Scope Decisions Made

- **English only** for first launch (Hindi/multilingual deferred to v2)
- **FAISS in-memory** confirmed over Qdrant Cloud (zero cost, <10ms retrieval)
- **e5-base-v2** (768-dim, English) instead of multilingual-e5-large (1024-dim) — 3x faster, smaller index
- **No LLM needed** for ingestion — embedding model runs locally, free
- **1 GB index budget** — actual usage: ~401 MB (well within budget)
- **No PDF parsing** for first launch — Kaggle datasets (75K files) are all PDFs, parked for later
- **QA pairs** (34,928 rows) saved as prompt data, not indexed in FAISS

---

## What Was Built

### 1. Data Ingestion Pipeline (`ingestion/`)

Complete 6-step pipeline: Parse → Chunk → Filter → Enrich → Embed → Index

| Module | File | Purpose |
|--------|------|---------|
| Config | `ingestion/config.py` | All paths, constants, data sources — single source of truth |
| Models | `ingestion/models.py` | `Chunk` + `ChunkMetadata` dataclasses shared across all modules |
| Parser | `ingestion/parsers/parquet_parser.py` | Loads HF parquets, auto-detects text/title columns |
| Chunker | `ingestion/chunkers/legal_chunker.py` | 700-token, 15% overlap, section-aware recursive splitting |
| Quality Filter | `ingestion/quality/filters.py` | SHA-256 dedup, min length (200 tokens), empty check |
| Enricher | `ingestion/enrichers/metadata.py` | Keyword-based domain classifier (10 legal domains) |
| Embedder | `ingestion/embedders/e5_embedder.py` | e5-base-v2 wrapper with proper "passage:"/"query:" prefixes |
| FAISS Builder | `ingestion/indexers/faiss_builder.py` | Build/save/load FAISS IndexFlatIP |
| BM25 Builder | `ingestion/indexers/bm25_builder.py` | Build/save/load BM25Okapi keyword index |

### 2. Pipeline Entry Point (`scripts/build_index.py`)

```bash
python3 scripts/build_index.py --all      # Full build
python3 scripts/build_index.py --list     # List sources
python3 scripts/build_index.py --sources sc_chunked central_acts  # Specific sources
```

### 3. CLI Search Tester (`scripts/search_test.py`)

```bash
python3 scripts/search_test.py "Can my landlord evict me?"           # Hybrid search
python3 scripts/search_test.py "Section 138 NI Act" --mode bm25     # Keyword only
python3 scripts/search_test.py "tenant rights" --mode faiss          # Semantic only
python3 scripts/search_test.py --interactive                         # Keep querying
```

### 4. Architecture Docs

- `docs/04_FIRST_LAUNCH_ARCHITECTURE.md` — Simplified MVP architecture (vs full-scale in 03)
- `docs/05_INGESTION_FLOW.md` — Detailed ingestion pipeline flow with diagrams
- `docs/diagrams/09_first_launch_architecture.mmd` — Mermaid diagram

### 5. Updated Config Files

- `requirements.txt` — Added FAISS, BM25, tiktoken; removed Qdrant, LangChain, LlamaIndex, scrapers
- `.gitattributes` — Added LFS tracking for `.faiss`, `.pkl`, `.npy` files
- `TRACKER.md` — Updated pipeline status, next steps, blockers

---

## Pipeline Run Results

**Executed**: `python3 scripts/build_index.py --all`
**Duration**: 17.5 minutes

### Data Processed

| Step | Count |
|------|-------|
| Documents parsed | 24,813 |
| Chunks after splitting | 55,508 |
| Chunks after quality filter | **35,858** |
| Dropped (too short) | 18,568 |
| Dropped (duplicates) | 1,082 |

### Chunks by Source

| Source | Chunks |
|--------|--------|
| Central Acts (883 acts) | 21,174 |
| Arunachal Pradesh Acts | 5,444 |
| Andhra Pradesh Acts | 3,303 |
| SC Judgments (HF pre-chunked) | 3,222 |
| Andaman & Nicobar Acts | 2,109 |
| Legal Chunks (HF) | 606 |

### Chunks by Legal Domain

| Domain | Chunks |
|--------|--------|
| Property | 15,398 |
| Criminal | 6,490 |
| Labour | 3,416 |
| General | 3,166 |
| RTI | 2,963 |
| Consumer | 1,459 |
| Family | 1,011 |
| Constitutional | 945 |
| Tax | 722 |
| Motor Accident | 188 |
| Cheque Bounce | 100 |

### Index Files Generated

| File | Size |
|------|------|
| `data/index/index.faiss` | 105.1 MB |
| `data/index/bm25.pkl` | 84.7 MB |
| `data/index/metadata.pkl` | 106.0 MB |
| `data/index/embeddings.npy` | 105.1 MB |
| **Total** | **~401 MB** |

---

## Search Tests (All Passing)

| Query | Top Result | Domain | Score |
|-------|-----------|--------|-------|
| "Can my landlord evict me without notice?" | Central Act — eviction notice provisions | property | 0.0164 |
| "what are the rights of a tenant in India?" | Arunachal Tenancy Act — tenant rights | property | 0.0315 |
| "cheque bounce under Section 138" | NI Act Section 138 — cheque dishonour | cheque_bounce | 0.0323 |
| "how to file FIR in India" | Anticipatory bail / FIR quashing provisions | criminal | 0.0315 |

---

## What's Next

### Immediate (Next Session)

1. **Build RAG chain** — Connect FAISS retrieval → Claude Sonnet for answer generation
   - Needs: Anthropic API key (sign up at console.anthropic.com)
   - Build: Hybrid search (RRF) → context assembly → system prompt → Claude → citation injection
   - Test: CLI query → full generated answer with citations

2. **Build FastAPI backend** — `/query`, `/document/generate`, `/scheme/check` endpoints

### After That

3. Build Next.js chat UI (Person B)
4. WhatsApp Business API integration
5. Build scrapers for remaining data (NCDRC, RTI, Delhi HC PDFs)
6. Add Kaggle SC judgment PDFs (need PDF parser)
7. Test 100 real queries, tune prompts
8. Beta launch

### Blockers

| Blocker | Status |
|---------|--------|
| Anthropic API key | Needed for RAG chain (next session) |
| Kaggle PDFs are not text files | Deferred — need PDF parser for post-launch |
| Sarvam AI | Deferred — English only for launch |

---

## File Tree (New/Modified)

```
Modified:
  requirements.txt
  .gitattributes
  TRACKER.md

New:
  TaskDone_21_june.md              ← This file
  ingestion/__init__.py
  ingestion/config.py
  ingestion/models.py
  ingestion/parsers/__init__.py
  ingestion/parsers/parquet_parser.py
  ingestion/chunkers/__init__.py
  ingestion/chunkers/legal_chunker.py
  ingestion/quality/__init__.py
  ingestion/quality/filters.py
  ingestion/enrichers/__init__.py
  ingestion/enrichers/metadata.py
  ingestion/embedders/__init__.py
  ingestion/embedders/e5_embedder.py
  ingestion/indexers/__init__.py
  ingestion/indexers/faiss_builder.py
  ingestion/indexers/bm25_builder.py
  scripts/build_index.py
  scripts/search_test.py
  docs/04_FIRST_LAUNCH_ARCHITECTURE.md
  docs/05_INGESTION_FLOW.md
  docs/diagrams/09_first_launch_architecture.mmd
  data/index/index.faiss
  data/index/bm25.pkl
  data/index/metadata.pkl
  data/index/embeddings.npy
  data/index/manifest.json
  data/processed/chunks.json
```

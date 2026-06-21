# Nyay.AI — Phase 1 Progress Tracker

> Last updated: 21 Jun 2026, 6:00 PM IST

---

## Project Setup

| Task | Status | Notes |
|------|--------|-------|
| Folder structure created | ✅ Done | `data/`, `scrapers/`, `api_clients/`, `ingestion/`, `config/`, `scripts/` |
| `requirements.txt` | ✅ Done | All Phase 1 deps listed |
| `.gitignore` | ✅ Done | Raw data excluded from git |
| `.env.example` | ✅ Done | All API key placeholders |
| `.env` | ✅ Done | Kaggle credentials set (gitignored) |
| `README.md` | ✅ Done | Project overview + quick start |
| `PHASE1_DATA_SOURCES.md` | ✅ Done | Full inventory of all data sources, APIs, URLs |
| `TRACKER.md` | ✅ Done | This file |
| `LaunchPlan.md` | ✅ Done | MVP scope, FAISS in-memory, 6-week timeline, 2-person split |
| `DataLoadPlan.md` | ✅ Done | Where data is stored, what to index, processing pipeline |
| Virtual environment (`venv/`) | ✅ Done | Python 3.9, deps installed |
| Download script (`scripts/download_datasets.py`) | ✅ Done | Supports 10 HF + 3 Kaggle datasets |
| Git LFS | ✅ Done | Parquet files tracked via LFS |
| Architecture docs (`docs/`) | ✅ Done | Use case, sequence diagrams, system architecture, ER diagram — all with PNGs |
| Kaggle API key | ✅ Done | `~/.kaggle/kaggle.json` configured |
| `first-launch` branch | ✅ Done | MVP branch separate from main |

---

## Data Collection — Pre-Built Datasets

### HuggingFace Datasets

| Dataset | Repo | Rows | Status |
|---------|------|------|--------|
| SC Judgements (Chunked) | `vihaannnn/Indian-Supreme-Court-Judgements-Chunked` | 20,961 | ✅ Downloaded |
| Indian Legal Acts | `geekyrakshit/indian-legal-acts` | 2,383 | ✅ Downloaded |
| MyScheme Govt Schemes | `shrijayan/gov_myscheme` | 3 | ✅ Downloaded |
| Legal Chunks (RAG-ready) | `ShreyasP123/Legal-Dataset-for-india` | 1,469 | ✅ Downloaded |
| Constitution of India (QA) | `nisaar/Constitution_of_India` | 933 | ✅ Downloaded |
| Constitution QA (3300 pairs) | `nisaar/Articles_Constitution_3300_Instruction_Set` | 3,311 | ✅ Downloaded |
| Indian Law Dataset | `viber1/indian-law-dataset` | 24,607 | ✅ Downloaded |
| Constitution + IPC Instruct | `RaagulQB/Indian-Constitution-And-IPC-Instruct` | 6,077 | ✅ Downloaded |
| Indian Judgements (Categorized) | `opennyaiorg/InJudgements_dataset` | — | ❌ Gated — needs HF token + access request |
| IL-TUR (Legal NLP) | `Exploration-Lab/IL-TUR` | — | ❌ Download failed — needs config |

### Kaggle Datasets

| Dataset | Repo | Files | Size | Status |
|---------|------|-------|------|--------|
| SC Judgments (Full PDFs) | `vangap/indian-supreme-court-judgments` | 48,295 PDFs + CSV | 5.4 GB | ✅ Downloaded |
| SC Judgments 1950-2025 | `adarshsingh0903/legal-dataset-sc-judgments-india-19502024` | 26,689 text files | 6.8 GB | ✅ Downloaded |
| High Court Cases in India | `saurabhshahane/high-court-cases-in-india` | 4 CSVs | 84 KB | ✅ Downloaded |

### Data on Disk — Total: ~12 GB

| Path | Size | Contents |
|------|------|----------|
| `data/raw/judgments/supreme_court/kaggle_1950_2024/` | 6.8 GB | 26,689 SC judgment text files (1950-2025) |
| `data/raw/judgments/supreme_court/kaggle_full/` | 5.4 GB | 48,295 SC judgment PDFs + metadata CSV |
| `data/raw/judgments/supreme_court/hf_chunked/` | 3.4 MB | 20,961 chunked SC judgments (parquet) |
| `data/raw/legislation/hf_acts/` | 37 MB | 2,383 acts with full Markdown text |
| `data/raw/legislation/hf_indian_law/` | 4.4 MB | 24,607 legal QA pairs |
| `data/raw/legislation/hf_constitution_qa/` | 2.4 MB | 3,311 Constitution QA pairs |
| `data/raw/legislation/hf_constitution_ipc_instruct/` | 1.1 MB | 6,077 Constitution+IPC QA |
| `data/raw/legislation/hf_constitution/` | 184 KB | 933 Constitution QA |
| `data/raw/judgments/hf_legal_chunks/` | 368 KB | 1,469 RAG-ready chunks |
| `data/raw/judgments/high_courts/kaggle_hc_cases/` | 84 KB | HC case metadata CSVs |
| `data/raw/schemes/hf_myscheme/` | 4 KB | Scheme PDF references |

---

## Data Collection — Scrapers

| Source | Target URL | Scraper Built? | Data Downloaded? | Priority |
|--------|-----------|----------------|------------------|----------|
| India Code (Central Acts) | indiacode.nic.in | ⬜ Not started | ⬜ | 🔴 HIGH |
| State Legislature Portals | varies by state | ⬜ Not started | ⬜ | 🟡 MEDIUM |
| BNS / BNSS / BSA (2024 criminal laws) | indiacode.nic.in | ⬜ Not started | ⬜ | 🔴 HIGH |
| Supreme Court (incremental) | sci.gov.in | ⬜ Not started | ⬜ | 🔴 HIGH |
| Delhi High Court | delhihighcourt.nic.in | ⬜ Not started | ⬜ | 🔴 HIGH |
| Bombay High Court | bombayhighcourt.gov.in | ⬜ Not started | ⬜ | 🔴 HIGH |
| Madras High Court | mhc.tn.gov.in/judis/ | ⬜ Not started | ⬜ | 🟡 MEDIUM |
| Karnataka High Court | karnatakajudiciary.kar.nic.in | ⬜ Not started | ⬜ | 🟡 MEDIUM |
| Calcutta High Court | calcuttahighcourt.gov.in | ⬜ Not started | ⬜ | 🟡 MEDIUM |
| NCDRC (Consumer Forum) | ncdrc.nic.in | ⬜ Not started | ⬜ | 🔴 HIGH |
| NCLT / NCLAT | nclt.gov.in | ⬜ Not started | ⬜ | 🟡 MEDIUM |
| ITAT | itat.gov.in | ⬜ Not started | ⬜ | 🟡 MEDIUM |
| RBI Circulars | rbi.org.in | ⬜ Not started | ⬜ | 🟡 MEDIUM |
| SEBI Circulars | sebi.gov.in | ⬜ Not started | ⬜ | 🟡 MEDIUM |
| GST / CBIC Circulars | cbic-gst.gov.in | ⬜ Not started | ⬜ | 🟡 MEDIUM |
| Labour Ministry | labour.gov.in | ⬜ Not started | ⬜ | 🟡 MEDIUM |
| MCA Circulars | mca.gov.in | ⬜ Not started | ⬜ | 🟡 MEDIUM |
| IRDAI | irdai.gov.in | ⬜ Not started | ⬜ | 🟡 MEDIUM |
| MyScheme Portal | myscheme.gov.in | ⬜ Not started | ⬜ | 🔴 HIGH |
| NALSA Legal Aid | nalsa.gov.in | ⬜ Not started | ⬜ | 🟡 MEDIUM |
| CIC / RTI Guidelines | cic.gov.in | ⬜ Not started | ⬜ | 🔴 HIGH |
| PIB Fact-Checks | pib.gov.in | ⬜ Not started | ⬜ | 🟢 LOW |

---

## Data Collection — API Integrations

| API | Sign Up URL | Key Obtained? | Client Built? | Priority |
|-----|-------------|---------------|---------------|----------|
| Indian Kanoon API | api.indiankanoon.org | ⬜ No | ⬜ No | 🔴 HIGH |
| kanoon.dev | docs.kanoon.dev | ⬜ No | ⬜ No | 🔴 HIGH |
| eCourtsIndia.com | ecourtsindia.com/api | ⬜ No | ⬜ No | 🟡 MEDIUM |
| Kleopatra (E-Courts) | court-api.kleopatra.io | ⬜ No | ⬜ No | 🟡 MEDIUM |
| Open Justice (ecourts scraper) | github.com/openjustice-in/ecourts | N/A (open source) | ⬜ No | 🟡 MEDIUM |

---

## Data Processing Pipeline

| Task | Status | Notes |
|------|--------|-------|
| PDF parser (PyMuPDF / Unstructured) | ⏸️ Deferred | Kaggle PDFs parked for post-launch |
| Text file reader | ⏸️ Deferred | Kaggle files are PDFs, not text |
| Parquet parser | ✅ Done | `ingestion/parsers/parquet_parser.py` — auto-detects text columns |
| Chunking pipeline (700 tok, 15% overlap) | ✅ Done | `ingestion/chunkers/legal_chunker.py` — section-boundary respecting |
| Quality filters (dedup, length, empty) | ✅ Done | `ingestion/quality/filters.py` — SHA-256 dedup |
| Metadata enrichment (doc_type, court, domain) | ✅ Done | `ingestion/enrichers/metadata.py` — keyword-based domain classifier |
| Embedding generation (e5-base-v2) | ✅ Done | `ingestion/embedders/e5_embedder.py` — 768-dim, English-only |
| FAISS index build (in-memory + disk save) | ✅ Done | `ingestion/indexers/faiss_builder.py` — IndexFlatIP |
| BM25 sparse index (rank_bm25) | ✅ Done | `ingestion/indexers/bm25_builder.py` — keyword search |
| Build pipeline script | ✅ Done | `scripts/build_index.py --all` — runs full pipeline |
| Hybrid search (RRF fusion) | ⬜ Not started | Combine dense + sparse at query time |
| Retrieval quality testing (100 test queries) | ⬜ Not started | Target: Recall@5 > 0.75 |

---

## Next Steps (In Order)

### Immediate Next Session
1. ~~Build chunking pipeline~~ ✅ Done
2. ~~Generate embeddings~~ ✅ Done (e5-base-v2, English only)
3. ~~Build FAISS index~~ ✅ Done
4. **Run `python scripts/build_index.py --all`** — execute the pipeline on actual data
5. **Build RAG chain** — query → hybrid retrieval (RRF) → Claude generation

### After That
6. Build FastAPI backend (`/query`, `/document/generate`, `/scheme/check`)
7. Build Next.js chat UI (Person B)
8. WhatsApp Business API integration
9. Build scrapers for remaining data (NCDRC, RTI, Delhi HC)
10. Test 100 real queries, tune prompts, beta launch

See `LaunchPlan.md` for full 6-week timeline and `DataLoadPlan.md` for data indexing strategy.

---

## Blockers & Dependencies

| Blocker | Impact | Resolution | Status |
|---------|--------|------------|--------|
| Kaggle API key | Can't download Kaggle datasets | Set up `~/.kaggle/kaggle.json` | ✅ Resolved |
| HF gated dataset access | Can't download InJudgements dataset | Request access on HuggingFace | ⬜ Pending |
| Anthropic API key | Can't test RAG chain | Sign up at console.anthropic.com | ⬜ Pending |
| Sarvam AI API key | Can't do Hindi translation | Sign up at sarvam.ai | ⏸️ Deferred (English only for launch) |
| API keys (Indian Kanoon, kanoon.dev) | Can't use structured APIs | Sign up at respective URLs | ⬜ Deferred to post-launch |

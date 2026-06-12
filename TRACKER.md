# Nyay.AI — Phase 1 Progress Tracker

> Last updated: 13 Jun 2026

---

## Project Setup

| Task | Status | Notes |
|------|--------|-------|
| Folder structure created | ✅ Done | `data/`, `scrapers/`, `api_clients/`, `ingestion/`, `config/`, `scripts/` |
| `requirements.txt` | ✅ Done | All Phase 1 deps listed |
| `.gitignore` | ✅ Done | Raw data excluded from git |
| `.env.example` | ✅ Done | All API key placeholders |
| `README.md` | ✅ Done | Project overview + quick start |
| `PHASE1_DATA_SOURCES.md` | ✅ Done | Full inventory of all data sources, APIs, URLs |
| Virtual environment (`venv/`) | ✅ Done | Python 3.9, deps installed |
| Download script (`scripts/download_datasets.py`) | ✅ Done | Supports HF + Kaggle with `--source` flag |

---

## Data Collection — Pre-Built Datasets

### HuggingFace Datasets

| Dataset | Repo | Rows | Status |
|---------|------|------|--------|
| SC Judgements (Chunked) | `vihaannnn/Indian-Supreme-Court-Judgements-Chunked` | 20,961 | ✅ Downloaded |
| Indian Legal Acts | `geekyrakshit/indian-legal-acts` | 2,383 (883 central + 1,500 state) | ✅ Downloaded |
| MyScheme Govt Schemes | `shrijayan/gov_myscheme` | 3 (PDF references) | ✅ Downloaded |
| Legal Chunks (RAG-ready) | `ShreyasP123/Legal-Dataset-for-india` | 1,469 | ✅ Downloaded |
| Indian Judgements (Categorized) | `opennyaiorg/InJudgements_dataset` | — | ❌ Gated — needs HF token + access request |

### Kaggle Datasets

| Dataset | Repo | Status |
|---------|------|--------|
| SC Judgments (Full PDFs) | `vangap/indian-supreme-court-judgments` | ⬜ Pending — needs Kaggle API key |
| SC Judgments 1950-2024 | `adarshsingh0903/legal-dataset-sc-judgments-india-19502024` | ⬜ Pending — needs Kaggle API key |

### Data on Disk

| Path | Size | Contents |
|------|------|----------|
| `data/raw/judgments/supreme_court/hf_chunked/` | 3.4 MB | 20,961 chunked SC judgments |
| `data/raw/legislation/hf_acts/` | 37 MB | 2,383 acts (central + state) with full Markdown |
| `data/raw/schemes/hf_myscheme/` | 4 KB | Scheme PDF references |
| `data/raw/judgments/hf_legal_chunks/` | 368 KB | 1,469 RAG-ready chunks |

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
| PDF parser (PyMuPDF / Unstructured) | ⬜ Not started | |
| HTML parser | ⬜ Not started | |
| Chunking pipeline (700 tok, 15% overlap) | ⬜ Not started | Section-boundary respecting |
| Metadata enrichment (doc_type, court, domain, year, etc.) | ⬜ Not started | |
| Embedding generation (multilingual-e5-large) | ⬜ Not started | |
| Qdrant collection setup (hybrid search) | ⬜ Not started | Dense + sparse vectors |
| BM25/BM42 sparse index | ⬜ Not started | |
| Retrieval quality testing (100 test queries) | ⬜ Not started | Target: Recall@5 > 0.75 |

---

## Next Steps (In Order)

### Immediate (This Week)
1. Set up Kaggle API key (`~/.kaggle/kaggle.json`) and download Kaggle SC judgment datasets
2. Request access to gated HF dataset (`opennyaiorg/InJudgements_dataset`)
3. Sign up for Indian Kanoon API + kanoon.dev API keys
4. Start building scrapers for HIGH priority sources:
   - India Code (central acts)
   - NCDRC (consumer forum orders)
   - CIC/RTI guidelines

### Next Week
5. Build Delhi HC + Bombay HC judgment scrapers
6. Build SC incremental scraper (daily new judgments)
7. Build MyScheme portal scraper
8. Start chunking + metadata enrichment pipeline for downloaded data

### Week 3-4
9. Set up Qdrant Cloud cluster (ap-south-1)
10. Generate embeddings (multilingual-e5-large) for all processed chunks
11. Load into Qdrant with hybrid search (dense + sparse)
12. Build and run 100 test queries — measure Recall@5 and MRR
13. Tune RRF weights for optimal hybrid retrieval

---

## Blockers & Dependencies

| Blocker | Impact | Resolution |
|---------|--------|------------|
| Kaggle API key needed | Can't download 85K+ SC judgment PDFs | User to set up `~/.kaggle/kaggle.json` |
| HF token + access request needed | Can't download categorized judgments dataset | User to request access on HuggingFace |
| API keys needed (Indian Kanoon, kanoon.dev, eCourts) | Can't use structured APIs for data | User to sign up at respective URLs |
| Qdrant Cloud account needed | Can't set up vector DB (Week 3) | Sign up at cloud.qdrant.io |
| Anthropic API key needed | Can't test RAG chain (Phase 2) | Sign up at console.anthropic.com |

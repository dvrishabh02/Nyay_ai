# Nyay.AI — Data Load Plan

> **Last updated**: 13 Jun 2026
> **Branch**: `first-launch`
> **Data budget for first launch**: ~1 GB (FAISS in-memory)
> **Total data on disk**: ~12 GB

---

## 1. Where Is Our Data Stored?

All raw data lives under `data/raw/` on disk. It is **gitignored for large files** (Kaggle PDFs) and **LFS-tracked for parquet files**.

```
data/raw/                                              TOTAL: ~12 GB
│
├── legislation/                                       45 MB
│   ├── hf_acts/                                       37 MB — 2,383 acts (Markdown)
│   │   ├── central.parquet                            23 MB — 883 central acts
│   │   ├── andhra_pradesh.parquet                     3.8 MB — 323 state acts
│   │   ├── arunachal_pradesh.parquet                  6.9 MB — 1,111 state acts
│   │   └── andaman_and_nicobar_islands.parquet        3.1 MB — 66 acts
│   ├── hf_indian_law/                                 4.4 MB — 24,607 legal QA pairs
│   │   └── train.parquet
│   ├── hf_constitution_qa/                            2.4 MB — 3,311 Constitution QA pairs
│   │   └── train.parquet
│   ├── hf_constitution_ipc_instruct/                  1.1 MB — 6,077 Constitution+IPC QA
│   │   └── train.parquet
│   └── hf_constitution/                               184 KB — 933 Constitution QA
│       └── train.parquet
│
├── judgments/                                         ~12 GB
│   ├── supreme_court/
│   │   ├── kaggle_1950_2024/                          6.8 GB — 26,689 text files (1950-2025)
│   │   │   └── supreme_court_judgments/
│   │   │       ├── 1950/                              61 files
│   │   │       ├── 1951/                              85 files
│   │   │       ├── ...                                (year-by-year folders)
│   │   │       ├── 2024/                              400 files
│   │   │       └── 2025/                              400 files
│   │   ├── kaggle_full/                               5.4 GB — 48,295 PDFs + metadata CSV
│   │   │   ├── judgments.csv                           8.2 MB — metadata for all judgments
│   │   │   └── pdfs/                                  48,294 individual PDF files
│   │   └── hf_chunked/                                3.4 MB — 20,961 pre-chunked passages
│   │       └── train.parquet
│   ├── hf_legal_chunks/                               368 KB — 1,469 RAG-ready chunks
│   │   └── train.parquet
│   ├── high_courts/
│   │   └── kaggle_hc_cases/                           84 KB — HC case metadata
│   │       ├── 7149_KEYS.csv
│   │       ├── 7149_METADATA.csv
│   │       ├── 7149_source_data.csv
│   │       └── NDAP_REPORT_7149.csv
│   ├── consumer_forum/                                (empty — scraper not built yet)
│   └── tribunals/                                     (empty — scraper not built yet)
│
├── schemes/                                           4 KB
│   └── hf_myscheme/                                   PDF references
│       └── train.parquet
│
├── circulars/                                         (empty — scraper not built yet)
└── citizen_resources/                                 (empty — scraper not built yet)
```

### Source Summary

| Source | Format | Files | Rows | Size | Downloaded From |
|--------|--------|-------|------|------|-----------------|
| Central Acts | Parquet (Markdown text) | 1 | 883 | 23 MB | HuggingFace: `geekyrakshit/indian-legal-acts` |
| State Acts (3 states) | Parquet | 3 | 1,500 | 14 MB | HuggingFace: `geekyrakshit/indian-legal-acts` |
| SC Judgments (Chunked) | Parquet | 1 | 20,961 | 3.4 MB | HuggingFace: `vihaannnn/Indian-Supreme-Court-Judgements-Chunked` |
| Legal Chunks (RAG-ready) | Parquet | 1 | 1,469 | 368 KB | HuggingFace: `ShreyasP123/Legal-Dataset-for-india` |
| Indian Law QA | Parquet | 1 | 24,607 | 4.4 MB | HuggingFace: `viber1/indian-law-dataset` |
| Constitution QA | Parquet | 1 | 933 | 184 KB | HuggingFace: `nisaar/Constitution_of_India` |
| Constitution QA (3300) | Parquet | 1 | 3,311 | 2.4 MB | HuggingFace: `nisaar/Articles_Constitution_3300_Instruction_Set` |
| Constitution+IPC Instruct | Parquet | 1 | 6,077 | 1.1 MB | HuggingFace: `RaagulQB/Indian-Constitution-And-IPC-Instruct` |
| Govt Scheme Refs | Parquet | 1 | 3 | 4 KB | HuggingFace: `shrijayan/gov_myscheme` |
| SC Judgments 1950-2025 | Text files | 26,689 | — | 6.8 GB | Kaggle: `adarshsingh0903/legal-dataset-sc-judgments-india-19502024` |
| SC Judgments (Full PDFs) | PDF + CSV | 48,295 | — | 5.4 GB | Kaggle: `vangap/indian-supreme-court-judgments` |
| HC Cases Metadata | CSV | 4 | — | 84 KB | Kaggle: `saurabhshahane/high-court-cases-in-india` |

---

## 2. First Launch — What We Index (1 GB FAISS Budget)

Not all 12 GB goes into the FAISS index. We pick the **highest-value data** that covers the top citizen legal problems.

### Tier 1: Index Everything (Direct to FAISS)

| Data | Rows | Why | Action |
|------|------|-----|--------|
| SC Judgments (Chunked HF) | 20,961 | Already chunked — RAG-ready | Load as-is |
| Legal Chunks (HF) | 1,469 | Already chunked — RAG-ready | Load as-is |
| Central Acts (Markdown) | 883 | Core legal text — every query needs this | Chunk into ~700 token segments |
| Constitution QA + Instruct | 10,321 | Pre-built QA pairs — great for answer quality | Load as-is |
| Indian Law QA | 24,607 | Covers broad legal topics | Load as-is |
| HC Cases Metadata | ~7,000 | Structured case data | Load as-is |
| SC Judgments Metadata CSV | ~48,000 | Case titles, dates, citations | Load as-is |

**Estimated FAISS size**: ~200 MB (embeddings) + ~100 MB (text + metadata) = **~300 MB**

### Tier 2: Parse + Chunk + Index (Top Priority)

| Data | Source | Action | Est. Size After Chunking |
|------|--------|--------|--------------------------|
| Top 5,000 SC Judgments (2020-2025) | `kaggle_1950_2024/` text files | Read text → chunk → embed | ~300 MB |
| Top 3 State Acts | `hf_acts/` state parquets | Chunk Markdown → embed | ~50 MB |
| SC Judgment PDFs (top 2,000 by citation) | `kaggle_full/pdfs/` | PDF → text → chunk → embed | ~200 MB |

**Estimated additional FAISS size**: ~150 MB

### Tier 3: Keep on Disk, Index Later (Post-Launch)

| Data | Size | When |
|------|------|------|
| Remaining 21,000 SC judgment text files (1950-2019) | 5 GB | After launch, batch index |
| Remaining 46,000 SC judgment PDFs | 5 GB | After launch, selective parsing |
| Consumer Forum Orders | 0 (not scraped yet) | Build scraper in Week 5 |
| RTI/CIC Guidelines | 0 (not scraped yet) | Build scraper in Week 5 |
| Delhi HC Judgments | 0 (not scraped yet) | Post-launch |
| RBI Circulars | 0 (not scraped yet) | Post-launch |

### Final Index Budget

```
Tier 1 (direct load):     ~300 MB
Tier 2 (parse + chunk):   ~150 MB
────────────────────────────────────
TOTAL FAISS INDEX:         ~450 MB  ← well within 1 GB RAM budget
BUFFER:                    ~550 MB  ← room for scraped data later
```

---

## 3. Processing Pipeline (How Data Becomes Searchable)

```
Raw Data → Parse → Clean → Chunk → Embed → FAISS Index
```

| Step | Tool | Details |
|------|------|---------|
| **Parse PDFs** | PyMuPDF + Tesseract OCR | Extract text from SC judgment PDFs |
| **Parse Text Files** | Python file read | Kaggle SC judgments are already text |
| **Parse Parquet** | pandas | HuggingFace datasets are structured |
| **Clean** | Custom Python | Remove headers, footers, page numbers, clean whitespace |
| **Chunk** | RecursiveCharacterTextSplitter | 700 tokens, 15% overlap, respect section boundaries |
| **Metadata** | Custom enrichment | Add: doc_type, court, year, domain, citation, source_url |
| **Embed** | multilingual-e5-large (1024 dim) | Dense vectors for semantic search |
| **Sparse Index** | rank_bm25 | BM25 tokens for keyword search |
| **Store** | FAISS + pickle | `.faiss` index + `.pkl` metadata, saved to disk |

### Chunk Metadata Schema

Every chunk in the index will have:

```json
{
  "chunk_id": "sc_2024_001_chunk_003",
  "text": "The tenant has a right to...",
  "doc_type": "judgment | act | constitution | scheme | circular",
  "court": "supreme_court | high_court | consumer_forum | null",
  "jurisdiction": "central | state_name",
  "domain": "property | consumer | criminal | labour | family | tax | constitutional",
  "year": 2024,
  "citation": "2024 INSC 640",
  "source": "kaggle_1950_2024",
  "source_file": "2024/case_001.txt",
  "chunk_index": 3,
  "total_chunks": 12
}
```

---

## 4. What Comes After First Launch

| Phase | Data Action | Size Added |
|-------|-------------|------------|
| **Post-Launch Week 1** | Index remaining 21K SC judgments (1950-2019) | +3 GB → move to Qdrant Cloud |
| **Post-Launch Week 2** | Build NCDRC consumer forum scraper, scrape 10K orders | +100 MB |
| **Post-Launch Week 3** | Build Delhi HC scraper, top 10K judgments | +200 MB |
| **Post-Launch Month 2** | RTI/CIC guidelines, Labour codes, RBI circulars | +60 MB |
| **Post-Launch Month 3** | Bombay HC, Madras HC, Karnataka HC scrapers | +500 MB |
| **Post-Launch Month 4** | Indian Kanoon API integration (paid), continuous ingestion | Ongoing |
| **Scale** | Migrate FAISS → Qdrant Cloud, full 127 GB corpus | Full corpus |

### When to Migrate from FAISS to Qdrant Cloud

| Trigger | Action |
|---------|--------|
| FAISS index > 1 GB RAM | Switch to Qdrant Cloud (free 1 GB tier) |
| Qdrant free tier exceeded | Upgrade to Qdrant paid ($25/mo for 4 GB) |
| Data > 10 GB indexed | Consider self-hosted Qdrant on AWS ECS |
| Daily queries > 10K | Add Redis caching for common queries |

---

## 5. Data Quality Checks (Before Indexing)

| Check | How | Accept Criteria |
|-------|-----|-----------------|
| Encoding | Detect charset, force UTF-8 | No garbled text |
| Language | Detect with langdetect | English or Hindi only for v1 |
| Length | Measure token count | Chunks: 200-1000 tokens |
| Duplicates | SHA-256 hash dedup | No duplicate chunks |
| Empty | Check for whitespace-only | No empty chunks |
| Legal relevance | Keyword check (act, section, court, etc.) | >80% chunks contain legal terms |

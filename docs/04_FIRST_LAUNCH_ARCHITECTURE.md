# Nyay.AI — First Launch Application Architecture

> **Branch**: `first-launch`
> **Team**: 2 people | **Timeline**: 6 weeks
> **Scope**: Hindi + English | Legal Q&A + 10 Doc Templates + Scheme Checker

---

## 1. High-Level Architecture (First Launch)

```
┌──────────────────────────────────────────────────────────────────────┐
│                          CLIENT LAYER                                │
│                                                                      │
│   ┌──────────────┐         ┌──────────────────────────────────┐      │
│   │  📱 WhatsApp  │         │  🌐 Next.js Web App (Vercel)    │      │
│   │  Meta Cloud   │         │  - Chat UI (mobile-first)       │      │
│   │  API Webhook  │         │  - Doc Generator UI             │      │
│   │               │         │  - Scheme Checker UI            │      │
│   │  Hindi + EN   │         │  - Landing Page                 │      │
│   └──────┬───────┘         └──────────┬───────────────────────┘      │
│          │                            │                              │
└──────────┼────────────────────────────┼──────────────────────────────┘
           │                            │
           ▼                            ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI on Railway/Render)                │
│                                                                      │
│   ┌──────────────────────────────────────────────────────────┐       │
│   │                    FastAPI Application                    │       │
│   │                                                          │       │
│   │  ┌─────────────┐  ┌────────────────┐  ┌──────────────┐  │       │
│   │  │ POST /query │  │ POST /document │  │ POST /scheme │  │       │
│   │  │             │  │   /generate    │  │   /check     │  │       │
│   │  │ Legal Q&A   │  │ 10 Templates   │  │ 100 Schemes  │  │       │
│   │  └──────┬──────┘  └───────┬────────┘  └──────┬───────┘  │       │
│   │         │                 │                   │          │       │
│   │         ▼                 ▼                   ▼          │       │
│   │  ┌─────────────────────────────────────────────────┐     │       │
│   │  │              Middleware Layer                    │     │       │
│   │  │  - Supabase Auth (JWT + Phone OTP)              │     │       │
│   │  │  - Quota Manager (10 free/day)                  │     │       │
│   │  │  - Rate Limiting                                │     │       │
│   │  │  - Langfuse Tracking                            │     │       │
│   │  └─────────────────────────────────────────────────┘     │       │
│   └──────────────────────────────────────────────────────────┘       │
│                                                                      │
│   ┌──────────────────────────────────────────────────────────┐       │
│   │                  IN-MEMORY RAG ENGINE                     │       │
│   │                                                          │       │
│   │  ┌──────────────┐    ┌──────────────┐                    │       │
│   │  │ FAISS Index  │    │ BM25 Index   │                    │       │
│   │  │ (~200 MB)    │    │ (rank_bm25)  │                    │       │
│   │  │ Dense vectors│    │ Sparse tokens│                    │       │
│   │  │ 1024-dim     │    │ Keyword      │                    │       │
│   │  └──────┬───────┘    └──────┬───────┘                    │       │
│   │         │                   │                            │       │
│   │         ▼                   ▼                            │       │
│   │  ┌──────────────────────────────────┐                    │       │
│   │  │  Hybrid Search (RRF Fusion)      │                    │       │
│   │  │  → Top-20 candidates             │                    │       │
│   │  │  → Rerank → Top-8 chunks         │                    │       │
│   │  └──────────────────────────────────┘                    │       │
│   │                                                          │       │
│   │  Index loaded from disk on startup (~10s)                │       │
│   │  Files: index.faiss + metadata.pkl + bm25.pkl            │       │
│   └──────────────────────────────────────────────────────────┘       │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
           │              │              │              │
           ▼              ▼              ▼              ▼
┌──────────────────────────────────────────────────────────────────────┐
│                       EXTERNAL SERVICES                              │
│                                                                      │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐      │
│   │ 🤖 Anthropic │  │ 🌍 Sarvam AI │  │ 🐘 Supabase          │      │
│   │ Claude Sonnet│  │ Hindi ↔ EN   │  │ - Auth (Phone OTP)   │      │
│   │              │  │ Translation  │  │ - PostgreSQL (Users,  │      │
│   │ Generation + │  │              │  │   Conversations,      │      │
│   │ Anti-halluc. │  │ Only for     │  │   Documents, Quotas)  │      │
│   │ Temp = 0     │  │ Hindi queries│  │ - Free tier           │      │
│   └──────────────┘  └──────────────┘  └──────────────────────┘      │
│                                                                      │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐      │
│   │ 💳 Razorpay  │  │ 📱 Meta      │  │ 📈 Langfuse          │      │
│   │ UPI + Cards  │  │ WhatsApp     │  │ LLM cost tracking    │      │
│   │ ₹49-199/doc  │  │ Business API │  │ Query quality        │      │
│   │              │  │ Webhooks     │  │ Free tier             │      │
│   └──────────────┘  └──────────────┘  └──────────────────────┘      │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 2. RAG Pipeline (First Launch — Simplified)

```
┌─────────────────────────────────────────────────────────────────────┐
│                         QUERY FLOW                                   │
│                                                                      │
│  User Query                                                          │
│      │                                                               │
│      ▼                                                               │
│  ┌─────────────────────────┐                                         │
│  │ 1. LANGUAGE DETECTION   │                                         │
│  │    langdetect library   │                                         │
│  │    Hindi → translate EN │◄── Sarvam AI API (Hindi only)           │
│  │    English → pass thru  │                                         │
│  └──────────┬──────────────┘                                         │
│             ▼                                                        │
│  ┌─────────────────────────┐                                         │
│  │ 2. QUERY UNDERSTANDING  │                                         │
│  │    - Domain detection   │  (property / consumer / criminal /      │
│  │    - Jurisdiction       │   labour / family / constitutional)     │
│  │    - Act/Section extract│  "Section 138 NI Act" → structured      │
│  └──────────┬──────────────┘                                         │
│             ▼                                                        │
│  ┌─────────────────────────────────────────────┐                     │
│  │ 3. HYBRID RETRIEVAL (in-memory)             │                     │
│  │                                             │                     │
│  │  ┌───────────────┐   ┌───────────────┐      │                     │
│  │  │ FAISS Dense   │   │ BM25 Sparse   │      │                     │
│  │  │ (e5-large     │   │ (rank_bm25    │      │                     │
│  │  │  embeddings)  │   │  keywords)    │      │                     │
│  │  └───────┬───────┘   └───────┬───────┘      │                     │
│  │          │                   │              │                     │
│  │          ▼                   ▼              │                     │
│  │  ┌───────────────────────────────────┐      │                     │
│  │  │ Reciprocal Rank Fusion (RRF)      │      │                     │
│  │  │ Combined score = Σ 1/(k + rank)   │      │                     │
│  │  └───────────────┬───────────────────┘      │                     │
│  │                  ▼                          │                     │
│  │          Top-20 Candidates                  │                     │
│  └─────────────────┬───────────────────────────┘                     │
│                    ▼                                                 │
│  ┌─────────────────────────┐                                         │
│  │ 4. RERANKING            │                                         │
│  │    Cross-encoder or     │  (lightweight — no Cohere for MVP,      │
│  │    score-based sorting  │   use sentence-transformers locally)    │
│  │    → Top-8 chunks       │                                         │
│  └──────────┬──────────────┘                                         │
│             ▼                                                        │
│  ┌─────────────────────────┐                                         │
│  │ 5. CONTEXT ASSEMBLY     │                                         │
│  │    - 8 chunks + metadata│                                         │
│  │    - Source citations    │                                         │
│  │    - Anti-hallucination  │                                         │
│  │      system prompt      │                                         │
│  └──────────┬──────────────┘                                         │
│             ▼                                                        │
│  ┌─────────────────────────┐                                         │
│  │ 6. LLM GENERATION      │                                         │
│  │    Claude Sonnet        │                                         │
│  │    Temperature = 0      │                                         │
│  │    "Only cite provided  │                                         │
│  │     sources. Say 'I     │                                         │
│  │     don't know' if not  │                                         │
│  │     in context."        │                                         │
│  └──────────┬──────────────┘                                         │
│             ▼                                                        │
│  ┌─────────────────────────┐                                         │
│  │ 7. POST-PROCESSING      │                                         │
│  │    - Citation injection  │  [Source: Section 138, NI Act 1881]    │
│  │    - Confidence score   │  HIGH / MEDIUM / LOW                    │
│  │    - Hindi translation  │◄── Sarvam AI (if user spoke Hindi)     │
│  │    - Legal disclaimer   │  "यह कानूनी सलाह नहीं है"               │
│  └──────────┬──────────────┘                                         │
│             ▼                                                        │
│       Final Response                                                 │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Data Ingestion Pipeline (Offline — Run Once, Rebuild Weekly)

```
┌─────────────────────────────────────────────────────────────────────┐
│                     DATA → INDEX PIPELINE                            │
│                     (python scripts/build_index.py)                  │
│                                                                      │
│  ┌────────────────────────────────────────────────┐                  │
│  │              RAW DATA (12 GB on disk)           │                  │
│  │                                                │                  │
│  │  HuggingFace Parquets   Kaggle Text Files      │                  │
│  │  - 883 Central Acts     - 5,000 SC Judgments    │                  │
│  │  - 20,961 SC chunks       (2020-2025 only)     │                  │
│  │  - 1,469 legal chunks   - Metadata CSV          │                  │
│  │  - 34,928 QA pairs                             │                  │
│  │  - 1,500 State Acts                            │                  │
│  └─────────────────┬──────────────────────────────┘                  │
│                    ▼                                                 │
│  ┌────────────────────────────────────────────────┐                  │
│  │              PARSE + CLEAN                      │                  │
│  │                                                │                  │
│  │  Parquet → pandas DataFrame                    │                  │
│  │  Text files → Python file read                 │                  │
│  │  Clean: remove headers, footers, page nums     │                  │
│  │  Encoding: force UTF-8                         │                  │
│  │  Language: keep English + Hindi only            │                  │
│  └─────────────────┬──────────────────────────────┘                  │
│                    ▼                                                 │
│  ┌────────────────────────────────────────────────┐                  │
│  │              CHUNK                              │                  │
│  │                                                │                  │
│  │  RecursiveCharacterTextSplitter                │                  │
│  │  - 700 tokens per chunk                        │                  │
│  │  - 15% overlap (105 tokens)                    │                  │
│  │  - Respect section/paragraph boundaries        │                  │
│  │  - Skip chunks < 200 tokens                    │                  │
│  │  - SHA-256 dedup                               │                  │
│  └─────────────────┬──────────────────────────────┘                  │
│                    ▼                                                 │
│  ┌────────────────────────────────────────────────┐                  │
│  │              ENRICH METADATA                    │                  │
│  │                                                │                  │
│  │  {                                             │                  │
│  │    "chunk_id": "sc_2024_001_chunk_003",        │                  │
│  │    "doc_type": "judgment | act | constitution", │                  │
│  │    "court": "supreme_court | high_court",      │                  │
│  │    "domain": "property | consumer | criminal", │                  │
│  │    "year": 2024,                               │                  │
│  │    "citation": "2024 INSC 640",                │                  │
│  │    "source": "kaggle_1950_2024"                │                  │
│  │  }                                             │                  │
│  └─────────────────┬──────────────────────────────┘                  │
│                    ▼                                                 │
│  ┌────────────────────────────────────────────────┐                  │
│  │              EMBED + INDEX                      │                  │
│  │                                                │                  │
│  │  multilingual-e5-large (1024 dim)              │                  │
│  │  ┌──────────────────┐  ┌──────────────────┐    │                  │
│  │  │ FAISS IndexFlat  │  │ BM25 (rank_bm25) │    │                  │
│  │  │ → index.faiss    │  │ → bm25.pkl       │    │                  │
│  │  │ (~200 MB)        │  │ (~50 MB)         │    │                  │
│  │  └──────────────────┘  └──────────────────┘    │                  │
│  │                                                │                  │
│  │  + metadata.pkl (chunk text + metadata dict)   │                  │
│  │                                                │                  │
│  │  Total on disk: ~450 MB                        │                  │
│  │  Total RAM at runtime: ~500 MB                 │                  │
│  └────────────────────────────────────────────────┘                  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 4. API Endpoints (First Launch)

```
FastAPI Backend — 3 core endpoints + 1 webhook

POST /api/v1/query
├── Headers: Authorization: Bearer <supabase_jwt>
├── Body: { "query": "...", "language": "hi|en" }
├── Flow: Auth → Quota check → RAG pipeline → Response
└── Response: { "answer": "...", "citations": [...], "confidence": "HIGH", "disclaimer": "..." }

POST /api/v1/document/generate
├── Headers: Authorization: Bearer <supabase_jwt>
├── Body: { "template": "rti|legal_notice|...", "fields": {...} }
├── Flow: Auth → Razorpay payment verify → Template fill → PDF generate
└── Response: { "document_url": "...", "price": 49 }

POST /api/v1/scheme/check
├── Headers: Authorization: Bearer <supabase_jwt>
├── Body: { "state": "...", "income": 25000, "category": "...", "occupation": "..." }
├── Flow: Auth → Match against scheme DB → Return eligible schemes
└── Response: { "eligible_schemes": [...], "total": 12 }

POST /api/v1/whatsapp/webhook
├── Source: Meta Cloud API
├── Flow: Parse message → Route to /query or /document → Send reply via Meta API
└── No auth (Meta signature verification instead)

GET /api/v1/health
└── Response: { "status": "ok", "index_loaded": true, "chunks": 65000 }
```

---

## 5. Deployment Architecture (First Launch)

```
┌──────────────────────────────────────────────────────────┐
│                    DEPLOYMENT                             │
│                                                          │
│  ┌─────────────────────┐    ┌─────────────────────┐      │
│  │  Vercel (Free)      │    │  Railway / Render    │      │
│  │                     │    │  ($5-25/mo)          │      │
│  │  Next.js Frontend   │    │                     │      │
│  │  - Landing page     │    │  FastAPI Backend     │      │
│  │  - Chat UI          │    │  - RAG engine        │      │
│  │  - Doc generator    │    │  - FAISS in-memory   │      │
│  │  - Scheme checker   │    │  - BM25 in-memory    │      │
│  │                     │    │  - WhatsApp webhook   │      │
│  │  Auto-SSL, CDN      │    │  - 1 GB RAM          │      │
│  └─────────┬───────────┘    └──────────┬──────────┘      │
│            │                           │                 │
│            │    HTTPS API calls        │                 │
│            └───────────────────────────┘                 │
│                                                          │
│  Index files stored in repo or S3:                       │
│  - index.faiss (~200 MB)                                 │
│  - metadata.pkl (~100 MB)                                │
│  - bm25.pkl (~50 MB)                                     │
│  Loaded into RAM on server startup (~10s)                │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## 6. What's NOT in First Launch (vs Full Architecture)

| Full Architecture (docs/03) | First Launch | Why Deferred |
|----------------------------|-------------|--------------|
| Qdrant Cloud | **FAISS in-memory** | Zero cost, faster, simpler |
| AWS ECS Fargate | **Railway / Render** | No DevOps overhead |
| CloudFront CDN | **Vercel built-in** | Free with Next.js |
| Cohere Reranker | **Local reranking** | Save API costs |
| Redis Cache | **No cache** | Optimize later |
| Scrapy spiders | **Manual data only** | Build scrapers in Week 5 |
| Voice (Bhashini) | **Text only** | Not core for launch |
| B2B API | **No B2B** | No enterprise clients yet |
| Lawyer Marketplace | **Not built** | Complex, needs onboarding |
| Case Status Tracker | **Not built** | Needs eCourts API |
| 10 languages | **Hindi + English** | Validate quality first |
| LlamaIndex + LangChain | **Custom Python** | Less overhead for simple RAG |

---

## 7. Cost Summary (Monthly)

```
Service                    Free Tier?    Estimated Cost
─────────────────────────────────────────────────────
FAISS (in-memory)          ✅ Free       ₹0
Vercel (Next.js)           ✅ Free       ₹0
Supabase (Auth + DB)       ✅ Free       ₹0
Langfuse (monitoring)      ✅ Free       ₹0
Railway/Render (backend)   Partial       ~₹2,000/mo
Anthropic Claude API       No            ~₹7,500/mo
Sarvam AI (Hindi)          No            ~₹2,500/mo
Razorpay                   Per txn       ~₹500/mo
WhatsApp Business API      Per msg       ~₹5,000/mo
─────────────────────────────────────────────────────
TOTAL                                    ~₹15,000/mo (~$180)
```

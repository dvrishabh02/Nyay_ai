# Nyay.AI — First Launch Plan

> **Branch**: `first-launch`
> **Team**: 2 people
> **Data Budget**: ~1 GB
> **Goal**: Ship a working WhatsApp + Web MVP that solves real problems for real users

---

## 1. What We're Launching (and What We're NOT)

### LAUNCH (MVP Features)

| # | Feature | Why It's In | Revenue | Effort |
|---|---------|-------------|---------|--------|
| 1 | **Legal Rights Navigator** | THE core product. User asks a question, gets a cited answer. | Drives adoption | High (RAG pipeline) |
| 2 | **Document Generator (10 templates)** | Immediate monetization. Users will pay ₹49–199 for a ready document. | ₹49–199/doc | Medium |
| 3 | **Scheme Eligibility Checker** | Massive user value with zero legal risk. 60% of Indians don't know their entitlements. | Free (drives retention) | Low (data already downloaded) |

### NOT LAUNCHING (Deferred to v2)

| Feature | Why Deferred |
|---------|-------------|
| Lawyer Connect Marketplace | Needs lawyer onboarding, verification, payment splits — too complex for 2 people |
| Case Status Tracker | Needs eCourts API integration + background workers + notification infra |
| Voice Input (Bhashini) | Nice-to-have, not core. Text-first is fine for launch. |
| B2B API | No enterprise clients yet. Build after proving consumer traction. |
| B2G Contracts | Sales cycle too long. Focus on organic users first. |
| 10 regional languages | Launch with **Hindi + English only**. Add languages after validating core RAG quality. |

### Launch Scope Summary

```
LAUNCH:  Hindi + English → WhatsApp bot + simple web UI → Legal Q&A + 10 doc templates + scheme checker
DEFER:   Lawyer marketplace, case tracker, voice, B2B/B2G, 8 other languages
```

---

## 2. Data Budget (~1 GB)

We have 1 GB to work with. Here's how we allocate it for maximum coverage of the most common citizen legal problems.

### Priority Data — What Citizens Actually Ask About

Based on consumer forum volumes, legal aid statistics, and Indian Kanoon search trends, the top citizen legal problem categories are:

1. **Tenant/Landlord disputes** (rent, deposit, eviction)
2. **Consumer complaints** (defective products, service deficiency, insurance denial)
3. **Employment/Labour** (salary, termination, PF/ESIC)
4. **Cheque bounce** (Section 138 NI Act)
5. **Property disputes** (land, registration, mutation)
6. **RTI applications** (how to file, what to ask)
7. **Government scheme eligibility**
8. **Family law basics** (maintenance, domestic violence protection)
9. **Criminal law basics** (FIR, bail, new BNS provisions)
10. **Motor vehicle accidents** (insurance claims, MACT)

### Data Allocation

| Data Source | What We Include | Est. Size | Status |
|-------------|----------------|-----------|--------|
| **Central Acts (India Code)** | All 883 central acts with full Markdown text | 23 MB | ✅ Already downloaded |
| **SC Judgments (Chunked)** | 20,961 pre-chunked SC judgment passages | 3.4 MB | ✅ Already downloaded |
| **Legal Chunks (RAG-ready)** | 1,469 pre-processed legal chunks | 368 KB | ✅ Already downloaded |
| **State Acts (Top 3 states)** | AP, Arunachal, Andaman acts already downloaded | 14 MB | ✅ Already downloaded |
| **Government Schemes** | MyScheme dataset (PDF references) | 4 KB | ✅ Already downloaded |
| **Consumer Protection Act + Rules** | Full CPA 2019 + rules + NCDRC guidelines | ~5 MB | 🔲 Scrape from India Code |
| **New Criminal Laws (BNS/BNSS/BSA)** | Full text of all 3 new codes | ~5 MB | 🔲 Extract from India Code dataset |
| **Top 5,000 Consumer Forum Orders** | NCDRC orders — most relevant for citizens | ~100 MB | 🔲 Scrape from ncdrc.nic.in |
| **RTI Act + CIC Guidelines** | RTI Act + top CIC orders + how-to guides | ~20 MB | 🔲 Scrape from cic.gov.in |
| **Labour Codes (4 new codes)** | Full text + key notifications | ~10 MB | 🔲 Scrape from labour.gov.in |
| **SC Judgments (Extended — Kaggle)** | Additional SC judgments for depth | ~200 MB | 🔲 Download from Kaggle |
| **Delhi HC Judgments (Top 10K)** | Most cited Delhi HC judgments | ~200 MB | 🔲 Scrape from delhihighcourt.nic.in |
| **Top Government Schemes (Full text)** | 100 most-used schemes with eligibility + application details | ~50 MB | 🔲 Scrape from myscheme.gov.in |
| **RBI Common Person Circulars** | Banking, loan, NBFC rules for citizens | ~30 MB | 🔲 Scrape from rbi.org.in |
| **Rent Control Acts (Top 5 states)** | Delhi, MH, KA, TN, WB rent laws | ~10 MB | 🔲 Scrape from state portals |
| **10 Legal Document Templates** | RTI, legal notice, consumer complaint, etc. | ~1 MB | 🔲 Create manually |
| **BUFFER** | Room for growth | ~328 MB | — |
| **TOTAL** | | **~672 MB** | Within 1 GB budget |

### What We're NOT Including (saves ~126 GB)

- ❌ All 25 High Court judgments (only Delhi HC top 10K)
- ❌ All tribunal orders (ITAT, NCLT, NCLAT)
- ❌ All regulatory circulars (only RBI common person)
- ❌ All state acts (only top 3-5 states for rent/property)
- ❌ SEBI, GST, MCA, IRDAI circulars (too niche for citizen MVP)

---

## 3. 10 Document Templates for Launch

| # | Template | Price | Use Case |
|---|----------|-------|----------|
| 1 | **RTI Application** | ₹49 | Most filed citizen legal action in India |
| 2 | **Consumer Complaint (District Forum)** | ₹99 | Defective products, service deficiency |
| 3 | **Legal Notice (General)** | ₹149 | Demand notice for any civil dispute |
| 4 | **Tenant Legal Notice** | ₹149 | Landlord not returning deposit, illegal eviction |
| 5 | **Cheque Bounce Notice (Sec 138 NI Act)** | ₹199 | 40 lakh+ cases/year |
| 6 | **Police Complaint / FIR Draft** | ₹49 | Help citizens write clear FIR complaints |
| 7 | **Employer Salary Demand Notice** | ₹149 | Unpaid salary, wrongful termination |
| 8 | **Insurance Claim Complaint** | ₹149 | Claim denial — massive consumer volume |
| 9 | **RERA Homebuyer Complaint** | ₹199 | 40 lakh+ RERA complaints pending |
| 10 | **Maintenance Application (Family Court)** | ₹149 | High volume, especially from women |

---

## 4. Tech Stack for Launch (Simplified)

For 2 people, we simplify aggressively:

| Layer | Launch Choice | Why |
|-------|--------------|-----|
| **Backend** | FastAPI (Python) | One person handles this |
| **Frontend** | Next.js + Tailwind (simple chat UI) | Other person handles this |
| **Vector DB** | FAISS in-memory + disk persistence | Zero cost, <10ms retrieval, no external dependency. Index saved to disk, loaded on startup (~10s). Migrate to Qdrant Cloud later if needed. |
| **LLM** | Claude Sonnet (Anthropic API) | Best instruction following, citation quality |
| **Indic Language** | Sarvam AI API (Hindi only for now) | Focus on Hindi quality first |
| **Embeddings** | multilingual-e5-large (self-hosted) | Free, excellent Hindi support |
| **Auth** | Supabase Auth (free tier) | JWT + phone OTP, zero infra |
| **Database** | Supabase PostgreSQL (free tier) | User data, conversations, quota |
| **WhatsApp** | Meta Cloud API | The distribution channel |
| **Payments** | Razorpay (for doc generation) | UPI + cards, lowest failure rates |
| **Hosting** | Railway.app or Render (start cheap) | Skip AWS complexity for MVP |
| **Monitoring** | Langfuse (free tier) | LLM cost tracking from day 1 |

**What we're NOT setting up for launch:**
- ❌ Qdrant Cloud / any external vector DB (FAISS in-memory is faster and free)
- ❌ AWS ECS Fargate (overkill for 2 people, use Railway/Render)
- ❌ Redis cache (optimize later)
- ❌ Background workers / cron scrapers (manual updates for now)
- ❌ CloudFront CDN (Vercel handles this for Next.js)

**In-Memory RAG Architecture:**
- FAISS index (~200 MB for dense vectors) loaded into RAM on server startup
- BM25 index (rank_bm25 library) for sparse/keyword search — also in-memory
- Combined via Reciprocal Rank Fusion (RRF) for hybrid search
- Index files saved to disk as `.faiss` + `.pkl` — version controlled or stored in S3
- Total RAM needed: ~500 MB (fits in Railway's 512 MB free tier or 1 GB paid)
- Retrieval latency: <10ms (vs ~50-100ms with Qdrant Cloud)

---

## 5. Work Split (2 People)

### Person A — Backend + RAG (the AI person)

| Week | Tasks |
|------|-------|
| **Week 1** | Build chunking pipeline for downloaded datasets. Generate embeddings with multilingual-e5-large. Build FAISS index + BM25 index in-memory. Save to disk. |
| **Week 2** | Build RAG chain: query understanding → hybrid retrieval → reranking → Claude generation. Anti-hallucination prompt. Confidence scoring. |
| **Week 3** | Build FastAPI backend: `/query`, `/document/generate`, `/scheme/check` endpoints. Supabase auth + quota. Hindi translation via Sarvam. |
| **Week 4** | WhatsApp Business API integration. Webhook handler. Conversation flow. Testing + prompt tuning. |
| **Week 5** | Scrape remaining data (NCDRC orders, RTI, Delhi HC top judgments). Rebuild FAISS + BM25 index with new data. |
| **Week 6** | Bug fixes. Prompt optimization. Launch prep. |

### Person B — Frontend + Templates + Growth

| Week | Tasks |
|------|-------|
| **Week 1** | Set up Next.js project. Build landing page. Design chat UI (mobile-first). |
| **Week 2** | Build web chat interface connected to FastAPI `/query` endpoint. Response rendering with citations. |
| **Week 3** | Build document generator UI. Create 10 legal document templates (research + draft). Razorpay integration. |
| **Week 4** | Build scheme eligibility checker UI. User auth flow (phone OTP via Supabase). Subscription page. |
| **Week 5** | Scrape government scheme details (100 schemes from myscheme.gov.in). Polish UI. |
| **Week 6** | Beta testing with 50 users. Feedback. Fix UX issues. Launch prep. |

### Shared Tasks (Both)

- Week 1: Sign up for all API keys (Anthropic, Sarvam, Supabase, Razorpay, Meta WhatsApp)
- Week 3: Write system prompt together (legal accuracy + anti-hallucination)
- Week 5: Test 100 real legal queries across domains. Measure quality.
- Week 6: Soft launch to 100 beta users. Public launch.

---

## 6. Launch Timeline

```
Week 1-2: Foundation
  ├── RAG pipeline working (Person A)
  ├── Web UI designed (Person B)
  └── All data loaded into Qdrant

Week 3-4: Integration
  ├── Backend API live (Person A)
  ├── Web chat + doc gen working (Person B)
  ├── WhatsApp bot connected (Person A)
  └── Payments working (Person B)

Week 5: Polish + Data
  ├── Scrape remaining data sources
  ├── Quality testing (100 queries)
  └── Beta launch (50 users)

Week 6: Launch
  ├── Fix beta feedback
  ├── Public launch (WhatsApp + Web)
  └── Community seeding (5 WhatsApp groups)
```

---

## 7. Launch Checklist

### Before Beta (Week 5)

- [ ] RAG pipeline returns accurate answers for top 10 legal domains
- [ ] Hindi + English working end-to-end
- [ ] WhatsApp bot responds within 5 seconds
- [ ] Web chat UI is mobile-responsive
- [ ] 10 document templates generating clean PDFs
- [ ] Scheme eligibility checker working for 100 schemes
- [ ] Razorpay payments working (test mode)
- [ ] Supabase auth working (phone OTP)
- [ ] Free quota enforcement (10 queries/day)
- [ ] Legal disclaimer on every response
- [ ] Confidence scoring + "consult a lawyer" escalation working
- [ ] Langfuse tracking all queries + costs

### Before Public Launch (Week 6)

- [ ] 50 beta users tested. Top 10 issues fixed.
- [ ] Razorpay live mode activated
- [ ] WhatsApp Business verified
- [ ] Domain purchased (nyay.ai or similar)
- [ ] Privacy policy + terms of service page
- [ ] "Information not advice" disclaimer legally reviewed
- [ ] Landing page with clear value proposition
- [ ] 5 demo videos (Hindi) showing real query resolution
- [ ] 3 WhatsApp groups identified for community seeding

---

## 8. Cost Estimate (Monthly — Post Launch)

| Service | Free Tier | Paid Estimate (1K users/day) |
|---------|-----------|------------------------------|
| FAISS (in-memory) | ₹0 (runs on same server) | ₹0 (no external service) |
| Anthropic (Claude) | — | ~$90/mo (10K queries × $0.003/query avg) |
| Sarvam AI | — | ~$30/mo (20% Hindi queries) |
| Supabase | Free tier | $0 (within free tier) |
| Railway/Render | Free tier / $5 | ~$25/mo (need 1 GB RAM for FAISS index) |
| Vercel (Next.js) | Free tier | $0 |
| WhatsApp Business API | Free to receive | ~₹5,000/mo (10K sent messages × ₹0.50) |
| Langfuse | Free tier | $0 |
| Domain | — | ~$12/year |
| **TOTAL** | | **~₹15,000/mo (~$180)** |

This is fundable from personal savings for 6+ months. No external funding needed for MVP validation.

**Note on in-memory approach:** FAISS index loads on server startup (~10s). If server restarts, index reloads from disk automatically. No data loss. When we outgrow 1 GB RAM (>100K chunks), we migrate to Qdrant Cloud — same embeddings, just swap the storage backend.

---

## 9. Success Metrics (First 30 Days Post-Launch)

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Total users (free) | 1,000 | Supabase user count |
| Daily active queries | 200 | Langfuse dashboard |
| Documents generated | 100 | Supabase query |
| Paid documents | 20 | Razorpay dashboard |
| Revenue | ₹5,000 | Razorpay dashboard |
| RAG accuracy (manual review) | >80% | Sample 50 queries/week |
| Average response time | <5 sec | Langfuse P95 latency |
| User retention (7-day) | >30% | Supabase analytics |

---

## 10. Risks for First Launch

| Risk | Mitigation |
|------|-----------|
| RAG gives wrong legal info | Confidence scoring + mandatory disclaimer + "consult lawyer" for LOW confidence |
| WhatsApp account suspended | Build web as primary backup from Day 1. Follow Meta's commerce policy strictly. |
| Claude API costs spike | Cache common queries. Set hard daily budget cap in Langfuse. Route simple queries to cheaper models later. |
| Nobody uses it | Community seeding in 5 WhatsApp groups. 3 Hindi YouTube demos. Target specific pain points ("landlord not returning deposit"). |
| Legal liability (Advocates Act) | Strict "information not advice" framing. Legal disclaimer on every response. Review with advocate advisor. |

---

## Files in This Branch

```
first-launch/
├── LaunchPlan.md          ← This file
├── PHASE1_DATA_SOURCES.md ← Full data source inventory (from main)
├── TRACKER.md             ← Progress tracker (from main)
├── docs/                  ← Architecture + diagrams (from main)
├── scripts/               ← Download scripts (from main)
├── data/raw/              ← Downloaded datasets (from main)
└── (new code will go here as we build)
```

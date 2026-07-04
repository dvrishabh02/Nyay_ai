# Nyay.AI — न्याय

**India's First Citizen-Facing Legal AI**

Empowering 100 Million Indians to understand and exercise their legal rights.

## What is Nyay.AI?

A WhatsApp-first, multilingual legal navigation platform powered by RAG (Retrieval-Augmented Generation) built on India's publicly available legal corpus. We give ordinary Indians instant, accurate access to their legal rights — in Hindi, English, and 8+ regional languages.

## Project Structure

```
Nyay_ai/
├── data/
│   ├── raw/                    # Raw downloaded data (gitignored)
│   │   ├── legislation/        # Central & state acts
│   │   ├── judgments/           # Court judgments
│   │   │   ├── supreme_court/
│   │   │   ├── high_courts/
│   │   │   ├── tribunals/
│   │   │   └── consumer_forum/
│   │   ├── circulars/          # Regulatory circulars
│   │   ├── schemes/            # Government schemes
│   │   └── citizen_resources/  # RTI, NALSA, PIB
│   └── processed/              # Chunked & embedded data
│       ├── chunks/
│       ├── embeddings/
│       └── metadata/
├── scrapers/                   # Scrapy spiders & pipelines
│   ├── spiders/
│   ├── pipelines/
│   └── utils/
├── api_clients/                # API client wrappers
├── ingestion/                  # Data processing pipeline
│   ├── parsers/                # PDF, HTML parsing
│   ├── chunkers/               # Text chunking logic
│   └── embedders/              # Embedding generation
├── config/                     # Configuration files
├── scripts/                    # Utility scripts (incl. prepare_hf_space.sh)
├── rag/                        # RAG chain: retriever, reranker, generator, pipeline
├── api/                        # FastAPI app (serves the RAG pipeline over HTTP)
├── frontend/                   # Next.js 15 + Tailwind chat UI
├── deploy/                     # Dockerfile + HF Space template for backend hosting
├── PHASE1_DATA_SOURCES.md      # Data source inventory
├── requirements.txt
└── .env.example
```

## Quick Start

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy env file and add your API keys
cp .env.example .env

# Download pre-built datasets
python scripts/download_datasets.py
```

## Running the App Locally (Backend + Frontend)

Prerequisites: the FAISS/BM25 indices under `data/index/` already built (see Quick
Start / `ingestion/`), a **Groq API key** (free tier works — [console.groq.com](https://console.groq.com)),
and **Node.js 18+** installed for the frontend.

### 1. Backend — FastAPI

```bash
# From the repo root, with the venv active
cp .env.example .env          # if you haven't already
# then edit .env and set GROQ_API_KEY=<your key>

uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

Wait for `Startup complete: pipeline ready.` in the logs (it loads the e5 embedder,
cross-encoder reranker, and FAISS/BM25 indices — takes a few seconds to under a
minute depending on your machine). Confirm it's up:

```bash
curl http://127.0.0.1:8000/health
# {"status":"ok","ready":true}
```

`--reload` restarts the server on code changes; logs print to that same terminal
(request lines, pipeline startup, generation logs). Leave this terminal running.

### 2. Frontend — Next.js

In a **second terminal**:

```bash
cd frontend
npm install
cp .env.local.example .env.local   # defaults to API_BASE_URL=http://localhost:8000 — fine for local dev
npm run dev
```

Open **http://localhost:3000** in your browser. Submitting a question calls
`frontend/app/api/chat/route.ts`, which proxies server-side to the FastAPI
`/query` endpoint above — no CORS setup needed since the browser only ever
talks to the Next.js server.

### Troubleshooting

- **Backend won't start / `GROQ_API_KEY is not set`** — add a real key to `.env` at the repo root.
- **Frontend shows "Could not reach the Nyay backend"** — the FastAPI server isn't running or isn't on the port `API_BASE_URL` in `frontend/.env.local` points to.
- **`/health` returns `"ready": false`** — the pipeline is still loading models/indices; wait and retry.

## Deploying for Free (so anyone with a URL can use it)

For the dev/demo stage: **frontend → Vercel** (free hobby tier), **backend → Hugging
Face Spaces** (free Docker CPU tier, no card required). HF Spaces was chosen over
tighter free tiers like Render's because the backend loads real models in-process
(e5 embedder + cross-encoder reranker) — that needs more RAM than a 512MB tier
comfortably gives. Trade-off: a free Space sleeps after inactivity, so the first
request after idle re-triggers a cold start (loading the indices again, a few
seconds to under a minute).

### A. Backend → Hugging Face Spaces

1. Create a free account at [huggingface.co](https://huggingface.co) if needed.
2. Go to **huggingface.co/new-space** → give it a name (e.g. `nyay-backend`) → SDK:
   **Docker** → hardware: **CPU basic (free)** → Create Space.
3. Generate a **User Access Token** with `write` scope: Settings →
   [Access Tokens](https://huggingface.co/settings/tokens). You'll use this as the
   git password in step 6.
4. Locally, build the deploy-only export (this repo's full git history includes the
   ~12GB raw legal corpus via LFS, which you don't want pushed to the Space):
   ```bash
   bash scripts/prepare_hf_space.sh
   # → writes a self-contained copy to dist/hf-space/ (code + indices only, ~300MB)
   ```
5. Turn that export into its own git repo and point it at the Space:
   ```bash
   cd dist/hf-space
   git init
   git lfs install
   git lfs track "*.faiss" "*.pkl"
   git add .
   git commit -m "Deploy backend"
   git remote add space https://huggingface.co/spaces/<your-username>/<space-name>
   ```
6. Push it (use your HF username + the access token from step 3 as the password
   when prompted):
   ```bash
   git push --force space main
   ```
7. In the Space's **Settings → Variables and secrets**, add a secret:
   `GROQ_API_KEY` = `<your Groq key>`.
8. The Space rebuilds automatically (watch the "Building" logs on the Space page).
   Once it shows **Running**, your backend is live at:
   `https://<your-username>-<space-name>.hf.space`
9. Verify:
   ```bash
   curl https://<your-username>-<space-name>.hf.space/health
   # {"status":"ok","ready":true}
   ```

To redeploy after backend code changes: re-run `scripts/prepare_hf_space.sh`, then
`cd dist/hf-space && git add -A && git commit -m "Update" && git push space main`.

### B. Frontend → Vercel

1. Push this repo to GitHub if it isn't already there (Vercel's import flow reads
   from a Git provider).
2. Create a free account at [vercel.com](https://vercel.com) (GitHub sign-in is
   easiest) → **Add New Project** → import this repo.
3. On the configure screen, set **Root Directory** to `frontend` — Vercel then
   auto-detects the Next.js app and needs no other build settings.
4. Add an **Environment Variable** (Production + Preview): `API_BASE_URL` =
   `https://<your-username>-<space-name>.hf.space` (the HF Space URL from step A9).
   This mirrors `frontend/.env.local.example` and stays server-side —
   `app/api/chat/route.ts` is the only thing that reads it.
5. Click **Deploy**. Vercel gives you a public URL like
   `https://<project>.vercel.app` — share that with anyone.
6. Open it, ask a real question, and confirm the answer comes back (first request
   may be slow if the HF Space was asleep — see the trade-off note above).

Every push to the repo's default branch redeploys the frontend automatically once
this is wired up.

## Phase 1 Focus (Weeks 1-4)

Building the foundational RAG corpus:
1. Download pre-built datasets (HuggingFace, Kaggle)
2. Build scrapers for India Code, Supreme Court, High Courts
3. Set up chunking + embedding pipeline
4. Load into Qdrant vector DB with hybrid search

## Tech Stack

- **RAG**: LlamaIndex + LangChain + Qdrant (hybrid BM25 + dense vector)
- **LLMs**: Claude Sonnet (primary) + Sarvam AI (Indic languages)
- **Embeddings**: multilingual-e5-large
- **Backend**: FastAPI (Python 3.11)
- **Frontend**: Next.js 15 + Tailwind CSS
- **Database**: Supabase (PostgreSQL)
- **Delivery**: WhatsApp Business API + Web

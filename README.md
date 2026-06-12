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
├── scripts/                    # Utility scripts
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

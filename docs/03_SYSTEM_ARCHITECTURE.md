# Nyay.AI — System Architecture

## 1. High-Level Architecture

![System Architecture](diagrams/06_system_architecture.png)

<details><summary>Mermaid source</summary>

```mermaid
graph TB
    subgraph "Client Layer"
        WA[📱 WhatsApp<br/>500M+ Indian users]
        WEB[🌐 Web App<br/>Next.js 15 + Tailwind]
        VOICE[🎤 Voice Input<br/>Bhashini API]
        B2BAPI[🔌 B2B API<br/>Corporate / Govt clients]
    end

    subgraph "API Gateway"
        CDN[☁️ CloudFront CDN]
        GW[🚪 FastAPI Gateway<br/>Rate limiting, Auth, Routing]
    end

    subgraph "Authentication & User Management"
        AUTH[🔐 Supabase Auth<br/>JWT + RLS]
        QUOTA[📊 Quota Manager<br/>Free: 10/day, Paid: unlimited]
    end

    subgraph "Core AI Pipeline"
        direction TB
        LANG[🌍 Language Detection<br/>+ Translation<br/>Sarvam AI / Google]
        QU[🧠 Query Understanding<br/>Domain + Jurisdiction +<br/>Act extraction]
        HYBRID[🔍 Hybrid Retrieval<br/>BM25 + Dense Vector]
        RERANK[📊 Cohere Reranker<br/>Top-8 selection]
        CTX[📋 Context Assembly<br/>Chunks + metadata + citations]
        GEN[🤖 LLM Generation<br/>Claude Sonnet<br/>Anti-hallucination prompt]
        CITE[📎 Citation Injection<br/>Source linking]
        CONF[⚖️ Confidence Scoring<br/>+ Escalation Logic]
    end

    subgraph "Data Layer"
        VDB[(🗄️ Qdrant Cloud<br/>Hybrid Search<br/>Dense + Sparse vectors)]
        DB[(🐘 Supabase PostgreSQL<br/>Users, conversations,<br/>documents, quotas)]
        S3[(📦 AWS S3<br/>Generated PDFs,<br/>document templates)]
        CACHE[(⚡ Redis Cache<br/>Common query responses)]
    end

    subgraph "Data Ingestion Pipeline"
        SCRAPERS[🕷️ Scrapy Spiders<br/>Courts, Acts, Circulars]
        PARSER[📄 Document Parser<br/>PyMuPDF + Unstructured +<br/>Tesseract OCR]
        CHUNKER[✂️ Chunking Pipeline<br/>700 tok, 15% overlap,<br/>section-boundary]
        META[🏷️ Metadata Enricher<br/>doc_type, court, domain,<br/>year, citation]
        EMBEDDER[🔢 Embedding Generator<br/>multilingual-e5-large<br/>1024 dimensions]
    end

    subgraph "Supporting Services"
        PAY[💳 Razorpay<br/>Subscriptions + One-time]
        TPL[📝 Template Engine<br/>50 legal doc templates]
        SCHEME[🏛️ Scheme Engine<br/>500+ govt schemes]
        ECOURT[⚖️ eCourts Integration<br/>Case status tracking]
        LAWYER[👨‍⚖️ Lawyer Marketplace<br/>Matching + Referral]
    end

    subgraph "Monitoring & Observability"
        LF[📈 Langfuse<br/>LLM cost, latency,<br/>quality metrics]
        SENTRY[🐛 Sentry<br/>Error tracking]
        DASH[📊 Admin Dashboard<br/>Analytics + Quality review]
    end

    WA -->|Webhook| GW
    WEB --> CDN --> GW
    VOICE --> GW
    B2BAPI --> GW

    GW --> AUTH --> QUOTA
    QUOTA --> LANG --> QU

    QU --> HYBRID
    HYBRID --> VDB
    HYBRID --> RERANK --> CTX --> GEN
    GEN --> CITE --> CONF

    CONF -->|HIGH| GW
    CONF -->|LOW| LAWYER

    GW --> PAY
    GW --> TPL --> S3
    GW --> SCHEME
    GW --> ECOURT
    GW --> LAWYER

    SCRAPERS --> PARSER --> CHUNKER --> META --> EMBEDDER --> VDB

    GW --> DB
    GW --> LF
    GW --> SENTRY
    LF --> DASH
```

</details>

---

## 2. RAG Pipeline Detail

![RAG Pipeline](diagrams/07_rag_pipeline.png)

<details><summary>Mermaid source</summary>

```mermaid
graph LR
    subgraph "Input Processing"
        Q[User Query] --> LD[Language Detect]
        LD --> TR[Translate to English<br/>if non-English]
        TR --> QE[Query Expansion<br/>+ Entity Extraction]
    end

    subgraph "Retrieval"
        QE --> DE[Dense Embedding<br/>multilingual-e5-large]
        QE --> SP[Sparse Tokens<br/>BM42]
        DE --> HY[Hybrid Search<br/>RRF Fusion<br/>α = tuned weight]
        SP --> HY
        HY --> MF[Metadata Filtering<br/>domain, jurisdiction,<br/>court level, year]
        MF --> TOP[Top-20 Candidates]
    end

    subgraph "Reranking"
        TOP --> CR[Cohere Reranker<br/>Cross-encoder scoring]
        CR --> T8[Top-8 Chunks<br/>selected]
    end

    subgraph "Generation"
        T8 --> CA[Context Assembly<br/>+ Source metadata]
        CA --> SYS[System Prompt<br/>Anti-hallucination rules<br/>Temperature = 0]
        SYS --> LLM[Claude Sonnet<br/>200K context window]
        LLM --> CI[Citation Injection<br/>Link every claim to source]
        CI --> CS[Confidence Scoring<br/>HIGH / MEDIUM / LOW]
    end

    subgraph "Output"
        CS --> TRO[Translate to<br/>User Language]
        TRO --> DIS[Add Disclaimer<br/>'Legal info, not advice']
        DIS --> OUT[Final Response]
    end
```

</details>

---

## 3. Infrastructure Layout (AWS ap-south-1)

<details><summary>Mermaid source</summary>

```mermaid
graph TB
    subgraph "AWS ap-south-1 (Mumbai)"
        subgraph "Compute"
            ECS1[ECS Fargate<br/>FastAPI Backend<br/>Task 1]
            ECS2[ECS Fargate<br/>FastAPI Backend<br/>Task 2]
            LAMBDA[Lambda<br/>Scraper triggers<br/>+ Cron jobs]
        end

        subgraph "Storage"
            RDS[(Supabase PostgreSQL<br/>User data, conversations)]
            S3_DOCS[(S3 Bucket<br/>Generated documents)]
            S3_CORPUS[(S3 Bucket<br/>Raw legal corpus)]
        end

        subgraph "CDN"
            CF[CloudFront<br/>Next.js frontend<br/>+ API caching]
        end

        subgraph "Networking"
            ALB[Application<br/>Load Balancer]
            VPC[VPC<br/>Private subnets]
        end
    end

    subgraph "External Services"
        QDRANT[Qdrant Cloud<br/>ap-south-1<br/>Vector DB]
        ANTHROPIC[Anthropic API<br/>Claude Sonnet]
        SARVAM[Sarvam AI API<br/>Indic Languages]
        COHERE[Cohere API<br/>Reranker]
        META[Meta Cloud API<br/>WhatsApp Business]
        RAZOR[Razorpay<br/>Payments]
        LANGFUSE[Langfuse Cloud<br/>LLM Observability]
    end

    subgraph "Clients"
        PHONE[📱 WhatsApp Users]
        BROWSER[🌐 Web Users]
    end

    PHONE --> META --> ALB
    BROWSER --> CF --> ALB
    ALB --> ECS1
    ALB --> ECS2
    ECS1 --> QDRANT
    ECS1 --> ANTHROPIC
    ECS1 --> SARVAM
    ECS1 --> COHERE
    ECS1 --> RDS
    ECS1 --> S3_DOCS
    ECS1 --> LANGFUSE
    ECS1 --> META
    ECS1 --> RAZOR
    LAMBDA --> S3_CORPUS
```

</details>

---

## 4. Data Model (Core Entities)

![Data Model](diagrams/08_data_model.png)

<details><summary>Mermaid source</summary>

```mermaid
erDiagram
    USERS {
        uuid id PK
        string phone_number UK
        string email
        string name
        string language_pref
        string state
        enum plan "free | basic | pro | premium"
        int daily_query_count
        timestamp created_at
    }

    CONVERSATIONS {
        uuid id PK
        uuid user_id FK
        string channel "whatsapp | web"
        string language
        timestamp started_at
        timestamp last_message_at
    }

    MESSAGES {
        uuid id PK
        uuid conversation_id FK
        enum role "user | assistant"
        text content
        string language
        float confidence_score
        int tokens_used
        float cost_usd
        int latency_ms
        json citations
        timestamp created_at
    }

    DOCUMENTS {
        uuid id PK
        uuid user_id FK
        uuid conversation_id FK
        string doc_type "rti | legal_notice | complaint"
        string status "draft | paid | downloaded"
        int price_inr
        string s3_url
        timestamp created_at
    }

    LAWYER_PROFILES {
        uuid id PK
        string name
        string bar_council_id UK
        string phone
        string email
        string city
        string state
        json specializations
        float rating
        int total_referrals
        boolean is_verified
        timestamp created_at
    }

    REFERRALS {
        uuid id PK
        uuid user_id FK
        uuid lawyer_id FK
        uuid conversation_id FK
        text case_brief
        string domain
        enum status "pending | accepted | declined | completed"
        int fee_inr
        float user_rating
        text user_review
        timestamp created_at
    }

    CASE_TRACKING {
        uuid id PK
        uuid user_id FK
        string cnr_number UK
        string court
        string case_status
        date next_hearing
        text last_order
        boolean notify_enabled
        timestamp last_checked
    }

    SCHEME_INQUIRIES {
        uuid id PK
        uuid user_id FK
        string state
        int monthly_income
        string occupation
        string category
        json eligible_schemes
        timestamp created_at
    }

    SUBSCRIPTIONS {
        uuid id PK
        uuid user_id FK
        enum plan "basic | pro | premium"
        string razorpay_sub_id
        int price_inr
        date start_date
        date end_date
        enum status "active | cancelled | expired"
    }

    USERS ||--o{ CONVERSATIONS : has
    CONVERSATIONS ||--o{ MESSAGES : contains
    USERS ||--o{ DOCUMENTS : generates
    USERS ||--o{ REFERRALS : requests
    LAWYER_PROFILES ||--o{ REFERRALS : receives
    USERS ||--o{ CASE_TRACKING : tracks
    USERS ||--o{ SCHEME_INQUIRIES : makes
    USERS ||--o{ SUBSCRIPTIONS : subscribes
    CONVERSATIONS ||--o{ DOCUMENTS : produces
    CONVERSATIONS ||--o{ REFERRALS : triggers
```

</details>

---

## 5. Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Next.js 15 + Tailwind CSS | Web app with server components |
| **Backend** | FastAPI (Python 3.11) | Async REST API |
| **Auth** | Supabase Auth (JWT + RLS) | User authentication |
| **Database** | Supabase PostgreSQL | User data, conversations, metadata |
| **Vector DB** | Qdrant Cloud (ap-south-1) | Hybrid BM25 + dense vector search |
| **Primary LLM** | Claude Sonnet (Anthropic) | Response generation |
| **Indic LLM** | Sarvam AI | Hindi/Tamil/Telugu language understanding |
| **Embeddings** | multilingual-e5-large | 1024-dim dense vectors |
| **Reranking** | Cohere Rerank API | Cross-encoder relevance scoring |
| **RAG Orchestration** | LlamaIndex + LangChain | Ingestion + query pipelines |
| **Scraping** | Scrapy + Playwright | Legal data collection |
| **Document Parsing** | Unstructured.io + PyMuPDF + Tesseract | PDF/HTML extraction |
| **WhatsApp** | Meta Cloud API | Primary delivery channel |
| **Payments** | Razorpay | Subscriptions + one-time payments |
| **Cloud** | AWS ap-south-1 (ECS Fargate) | Compute + storage |
| **CDN** | CloudFront | Frontend + API caching |
| **Monitoring** | Langfuse + Sentry | LLM observability + error tracking |
| **CI/CD** | GitHub Actions + Docker | Automated deployment |

---

## 6. Security & Compliance

| Concern | Approach |
|---------|----------|
| **Data Residency** | All data in AWS ap-south-1 (Mumbai). Qdrant in ap-south-1. |
| **User Data** | Supabase RLS — users can only access their own data |
| **API Keys** | Environment variables, never committed. `.env` gitignored. |
| **Legal Boundary** | System prompt enforces "information not advice". Disclaimer on every response. |
| **WhatsApp Policy** | No unsolicited messages. Compliance with Meta commerce policy. |
| **Hallucination** | Temperature=0. Citation-only rule. Confidence scoring. Lawyer escalation. |
| **Data Source** | All public data under NDSAP 2012 + RTI Act. Zero licensing costs. |

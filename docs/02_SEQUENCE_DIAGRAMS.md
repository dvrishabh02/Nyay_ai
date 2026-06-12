# Nyay.AI — Sequence Diagrams

## 1. Core RAG Query Flow (WhatsApp)

The primary interaction — a citizen asks a legal question via WhatsApp.

```mermaid
sequenceDiagram
    actor User as 👤 Citizen (WhatsApp)
    participant WA as WhatsApp<br/>Business API
    participant API as FastAPI<br/>Backend
    participant Auth as Supabase<br/>Auth
    participant QU as Query<br/>Understanding
    participant Trans as Sarvam AI /<br/>Translation
    participant VDB as Qdrant<br/>Vector DB
    participant Rerank as Cohere<br/>Reranker
    participant LLM as Claude<br/>Sonnet
    participant DB as Supabase<br/>PostgreSQL
    participant LF as Langfuse<br/>Observability

    User->>WA: Sends message in Hindi<br/>"मेरे मकान मालिक ने बिजली काट दी"
    WA->>API: Webhook POST /webhook/whatsapp
    API->>Auth: Verify user (phone number)
    Auth-->>API: User profile + quota status

    API->>API: Check free quota (10/day)
    alt Quota exceeded
        API->>WA: "Daily limit reached. Upgrade for ₹99/mo"
        WA->>User: Subscription prompt
    end

    API->>Trans: Detect language + translate to English
    Trans-->>API: "My landlord disconnected electricity"

    API->>QU: Extract: domain, jurisdiction, acts, urgency
    QU-->>API: {domain: "property/tenant",<br/>jurisdiction: "national",<br/>acts: ["Transfer of Property Act",<br/>"Electricity Act"],<br/>urgency: "medium"}

    API->>VDB: Hybrid search (dense + sparse)<br/>Filter: domain=property, type=judgment+act
    VDB-->>API: Top 20 candidate chunks

    API->>Rerank: Rerank 20 chunks for relevance
    Rerank-->>API: Top 8 reranked chunks with scores

    API->>API: Assemble context<br/>(8 chunks + metadata + citations)

    API->>LLM: System prompt (anti-hallucination rules)<br/>+ context + user query
    LLM-->>API: Grounded answer with citations<br/>+ confidence score: 0.91

    API->>API: Inject citation links<br/>+ append legal disclaimer

    API->>Trans: Translate response to Hindi
    Trans-->>API: Hindi response

    API->>DB: Log: query, response, tokens,<br/>confidence, latency
    API->>LF: Track: cost, latency, quality metrics

    API->>WA: Send formatted response
    WA->>User: Legal information in Hindi<br/>with citations + disclaimer<br/>+ follow-up options
```

---

## 2. Document Generation Flow

When a citizen needs a legal document (e.g., consumer complaint, RTI, legal notice).

```mermaid
sequenceDiagram
    actor User as 👤 Citizen
    participant UI as WhatsApp /<br/>Web UI
    participant API as FastAPI<br/>Backend
    participant LLM as Claude<br/>Sonnet
    participant TPL as Template<br/>Engine
    participant PAY as Razorpay
    participant DB as Supabase<br/>PostgreSQL
    participant S3 as AWS S3<br/>Storage

    User->>UI: "Generate a consumer complaint<br/>against my landlord"
    UI->>API: POST /api/document/generate

    API->>API: Extract context from<br/>conversation history

    API->>LLM: Generate document fields<br/>from conversation context
    LLM-->>API: {complainant_name, respondent_name,<br/>facts, relief_sought, applicable_sections}

    API->>TPL: Select template: "consumer_complaint"<br/>+ fill extracted fields
    TPL-->>API: Draft document (Markdown)

    API->>UI: Preview document
    UI->>User: "Here's your draft. Review and edit."
    User->>UI: Approves (or edits and approves)

    API->>API: Check document pricing
    alt Paid document (₹49-₹499)
        API->>PAY: Create Razorpay order
        PAY-->>API: Order ID + payment link
        API->>UI: Payment prompt
        UI->>User: Razorpay payment page
        User->>PAY: Completes payment (UPI/Card)
        PAY->>API: Webhook: payment success
    end

    API->>TPL: Render final PDF
    TPL-->>API: PDF document

    API->>S3: Store PDF
    S3-->>API: Download URL (time-limited)

    API->>DB: Log: doc_type, user, payment, timestamp
    API->>UI: Download link
    UI->>User: "Your document is ready. Download here."
```

---

## 3. Lawyer Connect & Referral Flow

When the system connects a citizen with a verified advocate.

```mermaid
sequenceDiagram
    actor User as 👤 Citizen
    actor Lawyer as ⚖️ Lawyer
    participant UI as WhatsApp /<br/>Web UI
    participant API as FastAPI<br/>Backend
    participant LLM as Claude<br/>Sonnet
    participant DB as Supabase<br/>PostgreSQL
    participant NOTIFY as Notification<br/>Service
    participant PAY as Razorpay

    User->>UI: "I need a lawyer for this"
    UI->>API: POST /api/lawyer/connect

    API->>LLM: Generate structured case brief<br/>from conversation history
    LLM-->>API: {case_type, facts_summary,<br/>applicable_laws, documents_prepared,<br/>urgency, location}

    API->>DB: Query verified lawyers<br/>Filter: domain + city + rating + availability
    DB-->>API: Matched lawyers (ranked)

    API->>UI: Show top 3 lawyer profiles<br/>with ratings, fees, specialization
    UI->>User: Lawyer cards with details

    User->>UI: Selects Advocate Sharma
    UI->>API: POST /api/lawyer/refer

    API->>DB: Create referral record<br/>(status: pending)

    API->>NOTIFY: Send referral to lawyer<br/>(WhatsApp + email)
    NOTIFY->>Lawyer: "New referral: Tenant dispute<br/>in Delhi. View brief."

    Lawyer->>API: GET /api/lawyer/referral/{id}
    API-->>Lawyer: Full case brief +<br/>documents + conversation summary

    alt Lawyer accepts
        Lawyer->>API: POST /api/lawyer/referral/{id}/accept
        API->>DB: Update referral status: accepted
        API->>NOTIFY: Notify citizen
        NOTIFY->>User: "Advocate Sharma accepted.<br/>Contact: +91-XXXXX"

        API->>PAY: Charge lawyer referral fee<br/>(₹500-₹2,500)
        PAY-->>API: Payment confirmed
    else Lawyer declines
        Lawyer->>API: POST /api/lawyer/referral/{id}/decline
        API->>DB: Update status: declined
        API->>API: Auto-refer to next matched lawyer
    end

    Note over User,Lawyer: After consultation
    User->>API: POST /api/lawyer/rate<br/>{rating: 4.5, review: "Very helpful"}
    API->>DB: Update lawyer rating
```

---

## 4. Government Scheme Eligibility Flow

```mermaid
sequenceDiagram
    actor User as 👤 Citizen
    participant UI as WhatsApp /<br/>Web UI
    participant API as FastAPI<br/>Backend
    participant SE as Scheme<br/>Engine
    participant VDB as Qdrant<br/>Vector DB
    participant DB as Supabase<br/>PostgreSQL

    User->>UI: "What government schemes<br/>can I apply for?"
    UI->>API: POST /api/schemes/check

    API->>UI: Ask eligibility questions
    UI->>User: "Please share:<br/>1. State<br/>2. Monthly income<br/>3. Occupation<br/>4. Category (SC/ST/OBC/General)<br/>5. Gender<br/>6. Age"

    User->>UI: "Maharashtra, ₹15,000/mo,<br/>farmer, OBC, Male, 35"
    UI->>API: User profile data

    API->>SE: Match eligibility criteria<br/>against 500+ schemes
    SE->>VDB: Retrieve scheme documents<br/>matching profile
    VDB-->>SE: Relevant scheme chunks

    SE->>SE: Rule-based eligibility check<br/>(income limits, category, state, age)
    SE-->>API: 12 eligible schemes found

    API->>UI: Formatted scheme list
    UI->>User: "You are eligible for 12 schemes:<br/><br/>1. PM-KISAN (₹6,000/year)<br/>   ✅ Eligible - farmer + income match<br/>   📋 Apply: pmkisan.gov.in<br/><br/>2. PM Fasal Bima Yojana<br/>   ✅ Eligible - farmer<br/>   📋 Apply: pmfby.gov.in<br/><br/>... 10 more"

    User->>UI: "Tell me more about PM-KISAN"
    UI->>API: GET /api/schemes/{id}
    API->>VDB: Retrieve full scheme details
    VDB-->>API: Scheme document chunks

    API->>UI: Detailed scheme info
    UI->>User: "PM-KISAN details:<br/>- Benefit: ₹6,000/year in 3 installments<br/>- Documents needed: Aadhaar, land records<br/>- How to apply: [step-by-step]<br/>- Helpline: 155261"

    API->>DB: Log scheme inquiry
```

---

## 5. Data Ingestion Pipeline (Backend)

How new legal documents flow from source to vector DB.

```mermaid
sequenceDiagram
    participant SCHED as AWS EventBridge<br/>Scheduler
    participant SCRAPER as Scrapy<br/>Spiders
    participant SOURCE as Legal Data<br/>Sources
    participant PARSER as Document<br/>Parser
    participant CHUNKER as Chunking<br/>Pipeline
    participant EMBED as Embedding<br/>Model
    participant VDB as Qdrant<br/>Vector DB
    participant LF as Langfuse<br/>Monitoring

    SCHED->>SCRAPER: Trigger daily scrape job

    par Parallel scraping
        SCRAPER->>SOURCE: Scrape sci.gov.in (SC judgments)
        SOURCE-->>SCRAPER: New PDFs since last run
    and
        SCRAPER->>SOURCE: Scrape Delhi HC
        SOURCE-->>SCRAPER: New judgment PDFs
    and
        SCRAPER->>SOURCE: Scrape RBI circulars
        SOURCE-->>SCRAPER: New circular PDFs
    end

    SCRAPER->>SCRAPER: Deduplicate by SHA-256 hash
    SCRAPER->>PARSER: Send new documents

    PARSER->>PARSER: PyMuPDF: Extract text from PDF
    PARSER->>PARSER: Unstructured.io: Parse HTML
    PARSER->>PARSER: Tesseract OCR: Scanned docs

    PARSER->>CHUNKER: Clean text documents
    CHUNKER->>CHUNKER: Split into 700-token chunks<br/>(15% overlap, section-boundary respecting)
    CHUNKER->>CHUNKER: Enrich metadata per chunk:<br/>{doc_type, court, jurisdiction,<br/>domain, year, citation,<br/>acts_cited, is_binding, source_url}

    CHUNKER->>EMBED: Chunks + metadata
    EMBED->>EMBED: Generate dense vectors<br/>(multilingual-e5-large, 1024 dim)
    EMBED->>EMBED: Generate sparse vectors<br/>(BM42 for keyword matching)

    EMBED->>VDB: Upsert chunks with<br/>dense + sparse vectors + metadata
    VDB-->>EMBED: Confirmation

    EMBED->>LF: Log: docs_processed, chunks_created,<br/>embedding_time, errors
    LF-->>EMBED: Metrics recorded
```

---

## 6. Case Status Tracking Flow

```mermaid
sequenceDiagram
    actor User as 👤 Citizen
    participant UI as WhatsApp /<br/>Web UI
    participant API as FastAPI<br/>Backend
    participant ECOURTS as eCourts<br/>API
    participant DB as Supabase<br/>PostgreSQL
    participant CRON as Background<br/>Worker
    participant NOTIFY as WhatsApp<br/>Notifications

    User->>UI: "Track my case:<br/>CNR DLCT01-001234-2024"
    UI->>API: POST /api/case/track

    API->>ECOURTS: GET case status by CNR
    ECOURTS-->>API: {status: "Pending",<br/>next_hearing: "2024-08-15",<br/>last_order: "Notice issued",<br/>judge: "Hon. Justice Kumar",<br/>court: "Tis Hazari, Delhi"}

    API->>DB: Save tracking subscription<br/>(user_id, cnr, notify: true)

    API->>UI: Case status card
    UI->>User: "📋 Case DLCT01-001234-2024<br/>Status: Pending<br/>Next hearing: 15 Aug 2024<br/>Last order: Notice issued<br/>Judge: Hon. Justice Kumar<br/><br/>🔔 Notifications enabled"

    Note over CRON,ECOURTS: Daily background check
    CRON->>DB: Get all tracked cases
    DB-->>CRON: List of CNR numbers

    loop For each tracked case
        CRON->>ECOURTS: Check for updates
        ECOURTS-->>CRON: Updated status
        alt Status changed
            CRON->>DB: Update case record
            CRON->>NOTIFY: Send update notification
            NOTIFY->>User: "🔔 Case Update!<br/>New order uploaded.<br/>Next hearing: 22 Sep 2024"
        end
    end
```

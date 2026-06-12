# Nyay.AI — Phase 1: Data Sources & API Plan

## Overview
This document lists **every data source** we need to hit for building the RAG corpus.
Sources are grouped by layer (as per the business plan) with access method, URL, API availability, and priority.

---

## LAYER 1: Legislation & Statutes

### 1.1 India Code (Central Acts)
- **URL**: https://www.indiacode.nic.in/
- **What**: All 1,500+ central acts, amendments, bare acts (XML + PDF)
- **Access Method**: Web scraping (Scrapy). Acts browsable by year at `/handle/123456789/1362/browse?type=actyear`
- **API**: ❌ No official API. Scrape HTML/PDF.
- **Format**: HTML pages + PDF downloads
- **Volume**: ~2,500 documents, ~8 GB
- **Update Freq**: Monthly
- **Priority**: 🔴 HIGH — foundational corpus
- **Notes**: Also available as a curated HuggingFace dataset: `geekyrakshit/indian-legal-acts`

### 1.2 State Legislature Portals
- **URL (examples)**:
  - Maharashtra: https://maharashtra.gov.in/legislature
  - Karnataka: https://vidhansabha.kar.nic.in
  - Tamil Nadu: https://www.assembly.tn.gov.in/
  - Delhi: http://delhiassembly.nic.in/
- **What**: State-specific laws (Rent Control, Shops & Establishments, Agricultural Land Acts)
- **Access Method**: Web scraping per state portal (each has different structure)
- **API**: ❌ No API
- **Format**: PDF downloads
- **Priority**: 🟡 MEDIUM — Phase 1 focus on top 5 states (MH, KA, DL, TN, UP)

### 1.3 Ministry/Department Regulations
- **URLs**:
  - Labour Ministry: https://labour.gov.in/
  - MCA: https://www.mca.gov.in/
  - SEBI: https://www.sebi.gov.in/
  - RBI: https://www.rbi.org.in/
  - TRAI: https://www.trai.gov.in/
  - IRDAI: https://www.irdai.gov.in/
- **What**: Enabling legislation, rules, delegated regulations from each ministry
- **Access Method**: Scrape each ministry's "Acts & Rules" section
- **API**: ❌ No API (except SEBI has structured listing pages)
- **Priority**: 🟡 MEDIUM — start with Labour, MCA

### 1.4 New Criminal Laws (2024)
- **What**: BNS (Bharatiya Nyaya Sanhita), BNSS (Bharatiya Nagarik Suraksha Sanhita), BSA (Bharatiya Sakshya Adhiniyam)
- **URL**: Available on https://www.indiacode.nic.in/ (search by year 2023)
- **Access Method**: Same as India Code scraper
- **Priority**: 🔴 HIGH — critical for criminal law queries

---

## LAYER 2: Case Law (Judgments)

### 2.1 Supreme Court of India
- **URL**: https://www.sci.gov.in/
- **Judgments Page**: https://www.sci.gov.in/judgements-case-no/
- **What**: All SC judgments from 1950 onwards (~85,000+ judgments as PDFs)
- **Access Method**: Scrapy + PDF download pipeline
- **API**: ❌ No official API. Scrape judgment listing pages.
- **Format**: PDF
- **Volume**: ~85,000 docs, ~15 GB
- **Update Freq**: Daily
- **Priority**: 🔴 HIGH
- **Shortcut**: Kaggle datasets available:
  - `vangap/indian-supreme-court-judgments` — CSV metadata + PDF links
  - `adarshsingh0903/legal-dataset-sc-judgments-india-19502024` — preprocessed
  - HuggingFace: `vihaannnn/Indian-Supreme-Court-Judgements-Chunked` — already chunked!
  - HuggingFace: `opennyaiorg/InJudgements_dataset` — categorized judgments

### 2.2 High Court Judgments (Top 5 Priority)
| Court | URL | Notes |
|-------|-----|-------|
| Delhi HC | https://delhihighcourt.nic.in/web/judgement/fetch-data | Structured judgment search |
| Bombay HC | https://bombayhighcourt.gov.in/bhc/judgments | Search by date/judge/case |
| Madras HC | https://www.mhc.tn.gov.in/judis/ | JUDIS portal |
| Karnataka HC | https://karnatakajudiciary.kar.nic.in/ | Judgment search available |
| Calcutta HC | https://calcuttahighcourt.gov.in/ | Judgment portal |

- **Access Method**: Scrapy spiders per HC (each has different structure). Selenium for JS-heavy portals.
- **API**: ❌ No official API
- **Volume**: ~500,000 docs (top 5 HCs), ~60 GB
- **Priority**: 🔴 HIGH (Delhi, Bombay first)

### 2.3 eCourts (District + HC — Unified Portal)
- **Official Portal**: https://ecourts.gov.in/
- **What**: Case status, orders, hearing dates for District Courts + High Courts
- **Access Methods** (multiple options):

  #### Option A: Open Justice India (Free, Open Source)
  - **GitHub**: https://github.com/openjustice-in/ecourts
  - **Docs**: https://openjustice-in.github.io/ecourts/
  - **What**: Python library to scrape eCourts. Covers District Courts + HCs.
  - **Dataset**: 81 million case records already scraped
  - **Cost**: FREE
  - **Best for**: Bulk historical data

  #### Option B: eCourtsIndia.com API (Paid, Structured)
  - **URL**: https://ecourtsindia.com/api
  - **Docs**: https://ecourtsindia.com/api/docs
  - **Pricing**: https://ecourtsindia.com/api/pricing — ₹200 free credits on signup, pay-per-request
  - **Endpoints**: Search cases, fetch details, download orders (PDF)
  - **Best for**: Real-time case status, structured data

  #### Option C: Kleopatra / E-Courts India API (Paid)
  - **URL**: https://court-api.kleopatra.io (moved from eciapi.akshit.me)
  - **What**: Enterprise-grade API. District Courts, HCs, SC, NCLT, Consumer Forum.
  - **Pricing**: Free for non-commercial/research. Pay-per-request for commercial.
  - **Best for**: Production-grade integration

### 2.4 Indian Kanoon (Aggregated Case Law)
- **URL**: https://indiankanoon.org/
- **API**: ✅ YES — https://api.indiankanoon.org/
- **Docs**: https://api.indiankanoon.org/documentation/
- **Pricing**: https://api.indiankanoon.org/pricing/
  - ₹500 free credits on signup
  - Non-commercial: ₹10,000 free/month (requires verification)
  - Usage-based prepaid after that
- **Features**: Search, document retrieval, text fragments, AI tags, structural analysis (facts/issues/arguments/holding)
- **Best for**: Supplementary cross-reference, filling gaps in official portals
- **Priority**: 🟢 HIGH — easiest structured API access to Indian case law

### 2.5 kanoon.dev API (Modern Alternative)
- **URL**: https://docs.kanoon.dev/
- **What**: Modern REST API for Indian law — courts, cases, orders, insights, search
- **Endpoints**:
  - `GET /courts` — list all courts
  - `GET /cases` — list/search cases
  - `GET /cases/:id` — retrieve full case
  - `GET /orders` — list orders
  - `GET /orders/:id` — retrieve order
  - `GET /insights` — case insights (outcomes, causes)
  - `GET /search` — full-text search
- **Auth**: API key (Bearer token)
- **Priority**: 🟢 HIGH — structured, modern, easy to integrate

---

## LAYER 3: Tribunal Orders

### 3.1 ITAT (Income Tax Appellate Tribunal)
- **URL**: https://itat.gov.in/
- **Orders**: https://itat.gov.in/judicial/tribunalorders
- **Access Method**: Scrape order listing + PDF downloads
- **API**: ❌ No API
- **Priority**: 🟡 MEDIUM

### 3.2 NCLT / NCLAT (Company Law Tribunal)
- **URL**: https://nclt.gov.in/
- **Orders**: https://nclt.gov.in/order-judgement-date-wise-search
- **Archive**: https://archive.nclt.gov.in/exposed-order-judgements-page
- **Access Method**: Scrape date-wise/judge-wise listing + PDF downloads
- **API**: ❌ No API
- **Priority**: 🟡 MEDIUM

### 3.3 NCDRC (Consumer Forum — National)
- **URL**: https://ncdrc.nic.in/
- **What**: Consumer dispute orders — highly relevant for citizen-facing platform
- **Access Method**: Scrape order pages
- **Also**: e-Jagriti platform (https://e-jagriti.gov.in/) — newer consumer forum portal
- **API**: ❌ No API
- **Priority**: 🔴 HIGH — core use case for consumers

---

## LAYER 4: Regulatory Circulars & Guidelines

### 4.1 RBI (Reserve Bank of India)
- **Circulars Index**: https://www.rbi.org.in/scripts/BS_CircularIndexDisplay.aspx
- **Master Directions**: https://www.rbi.org.in/scripts/BS_ViewMasterCirculars.aspx
- **Master Circulars**: https://www.rbi.org.in/Scripts/BS_ViewMasterCirculardetails.aspx
- **Common Person**: https://www.rbi.org.in/commonperson/English/Scripts/MasterCircular.aspx
- **Access Method**: Scrape circular listing pages → download PDFs
- **API**: ❌ No API
- **Priority**: 🟡 MEDIUM

### 4.2 SEBI (Securities & Exchange Board)
- **Circulars**: https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=1&ssid=7
- **Regulations**: https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=1&ssid=3
- **Master Circulars**: https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=1&ssid=6
- **Access Method**: Scrape listing pages → download PDFs
- **API**: ❌ No API
- **Priority**: 🟡 MEDIUM

### 4.3 GST / CBIC
- **CBIC GST Circulars**: https://cbic-gst.gov.in/hindi/circulars.html
- **CGST Circulars (GST Council)**: https://gstcouncil.gov.in/cgst-circulars
- **CBIC Main**: https://www.cbic.gov.in/htdocs-cbec/gst/gstcirculars
- **Tax Info Portal**: https://taxinformation.cbic.gov.in/
- **Volume**: 2,000+ documents since 2017
- **API**: ❌ No API
- **Priority**: 🟡 MEDIUM

### 4.4 Labour Ministry
- **URL**: https://labour.gov.in/
- **What**: 4 Labour Codes notifications, EPF/ESIC circulars, minimum wage notifications
- **API**: ❌ No API
- **Priority**: 🟡 MEDIUM

### 4.5 MCA (Ministry of Corporate Affairs)
- **URL**: https://www.mca.gov.in/
- **What**: Company law interpretations, LLP rules, director liability
- **API**: ❌ No API
- **Priority**: 🟡 MEDIUM

### 4.6 IRDAI (Insurance Regulatory Authority)
- **URL**: https://www.irdai.gov.in/
- **What**: Insurance regulations — claim denial, mis-selling queries
- **API**: ❌ No API
- **Priority**: 🟡 MEDIUM — but high consumer relevance

---

## LAYER 5: Government Scheme Data

### 5.1 MyScheme Portal
- **URL**: https://www.myscheme.gov.in/
- **Find Scheme**: https://www.myscheme.gov.in/find-scheme
- **What**: 500+ central + state schemes with eligibility criteria
- **API**: Structured web portal (scrape-friendly)
- **HuggingFace Dataset**: `shrijayan/gov_myscheme` — 723 scheme PDFs already extracted!
- **Priority**: 🔴 HIGH — core feature (Scheme Eligibility Engine)

### 5.2 State Government Portals
- Maharashtra: https://mahaonline.gov.in/
- Karnataka: https://serviceonline.gov.in/
- Others vary by state
- **Priority**: 🟡 MEDIUM — after central schemes

### 5.3 PM India (Central Schemes)
- **URL**: https://www.pmindia.gov.in/
- **What**: All central schemes with FAQs, eligibility, application links
- **API**: ❌ No API
- **Priority**: 🟡 MEDIUM

### 5.4 DBT.gov.in (Direct Benefit Transfer)
- **URL**: https://dbt.gov.in/
- **What**: JAM Trinity data — scheme disbursement and coverage
- **Priority**: 🟢 LOW

---

## LAYER 6: Citizen-Specific Resources

### 6.1 PIB Fact-Checks
- **URL**: https://pib.gov.in/
- **What**: Government fact-checks and press releases
- **Access**: RSS feeds available
- **Priority**: 🟢 LOW

### 6.2 NALSA (Legal Aid Schemes)
- **URL**: https://nalsa.gov.in/
- **Legal Aid**: https://nalsa.gov.in/legal-aid/
- **Schemes**: https://nalsa.gov.in/preventive-strategic-legal-services-schemes/
- **What**: Who qualifies for free legal aid, how to apply
- **Priority**: 🟡 MEDIUM

### 6.3 CIC (RTI Guidelines)
- **URL**: https://cic.gov.in/
- **What**: Central Information Commission orders, RTI Act interpretation
- **Priority**: 🔴 HIGH — RTI is one of the highest-volume citizen legal actions

---

## PRE-BUILT DATASETS (Shortcuts for Phase 1)

These save weeks of scraping work:

| Dataset | Source | What | Size |
|---------|--------|------|------|
| `vangap/indian-supreme-court-judgments` | Kaggle | SC judgments metadata + PDFs | Large |
| `adarshsingh0903/legal-dataset-sc-judgments-india-19502024` | Kaggle | SC judgments 1950-2024 | Large |
| `vihaannnn/Indian-Supreme-Court-Judgements-Chunked` | HuggingFace | Already chunked SC judgments! | Ready for RAG |
| `opennyaiorg/InJudgements_dataset` | HuggingFace | Categorized Indian judgments | Labeled |
| `ShreyasP123/Legal-Dataset-for-india` | HuggingFace | Semantic chunks for RAG | Ready for RAG |
| `geekyrakshit/indian-legal-acts` | HuggingFace | Indian legal acts | Structured |
| `shrijayan/gov_myscheme` | HuggingFace | 723 MyScheme PDFs | Structured |
| Open Justice India | GitHub | 81M eCourts case records | Massive |

---

## THIRD-PARTY APIs (Structured Access)

| API | URL | Auth | Pricing | Best For |
|-----|-----|------|---------|----------|
| **Indian Kanoon API** | https://api.indiankanoon.org/ | Public-private key signing | ₹500 free, ₹10K/mo non-commercial | Case law search + docs |
| **kanoon.dev** | https://docs.kanoon.dev/ | Bearer token (API key) | TBD (contact) | Modern REST API for cases/orders |
| **eCourtsIndia.com** | https://ecourtsindia.com/api | Bearer token | ₹200 free credits, pay-per-request | Real-time case status |
| **Kleopatra (E-Courts)** | https://court-api.kleopatra.io | API key | Free for research, paid commercial | Enterprise court data |
| **Open Justice (ecourts)** | https://github.com/openjustice-in/ecourts | Open source | FREE | Bulk scraping toolkit |

---

## PHASE 1 EXECUTION PLAN (Weeks 1-4)

### Week 1: Quick Wins — Pre-built Datasets
1. Download HuggingFace datasets: `vihaannnn/Indian-Supreme-Court-Judgements-Chunked`, `geekyrakshit/indian-legal-acts`, `shrijayan/gov_myscheme`, `ShreyasP123/Legal-Dataset-for-india`
2. Download Kaggle SC judgments dataset
3. Sign up for Indian Kanoon API (get ₹500 free credits + apply for non-commercial ₹10K/mo)
4. Sign up for kanoon.dev API key
5. Sign up for eCourtsIndia.com API (₹200 free credits)
6. Store all raw data in structured folders in repo

### Week 2: Core Scrapers — Legislation
7. Build India Code scraper (Scrapy) — all central acts
8. Build BNS/BNSS/BSA scraper (or extract from India Code)
9. Build CIC/RTI scraper for RTI guidelines
10. Build NCDRC consumer forum order scraper

### Week 3: Case Law Scrapers
11. Build SC judgment scraper (or use Kaggle data + daily incremental scraper)
12. Build Delhi HC judgment scraper
13. Build Bombay HC judgment scraper
14. Test Indian Kanoon API for gap-filling

### Week 4: Regulatory + Schemes
15. Build RBI circulars scraper
16. Build SEBI circulars scraper
17. Build MyScheme scraper (or use HuggingFace dataset)
18. Build NALSA legal aid scraper
19. Consolidate all data → begin chunking + embedding pipeline

---

## API KEYS NEEDED (Sign Up List)

| Service | Sign Up URL | Cost |
|---------|-------------|------|
| Indian Kanoon API | https://api.indiankanoon.org/ | Free ₹500 + ₹10K/mo non-commercial |
| kanoon.dev | https://docs.kanoon.dev/ | Contact for key |
| eCourtsIndia.com | https://ecourtsindia.com/api | ₹200 free credits |
| Kleopatra | https://court-api.kleopatra.io | Free for research |
| Kaggle | https://www.kaggle.com/ | Free account for dataset downloads |
| HuggingFace | https://huggingface.co/ | Free account for dataset downloads |
